from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.models import User, LoginActivity  # Add LoginActivity here
from app.api.admin.admin_routes import check_admin

router = APIRouter()

@router.get("/analytics/registration-trends")
async def get_registration_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get user registration trends for the specified number of days"""
    try:
        # Use current date instead of future date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"Fetching registrations from {start_date} to {end_date}")  # Debug log
        
        daily_registrations = (
            db.query(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            )
            .filter(User.created_at >= start_date)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
            .all()
        )
        
        print(f"Found registrations: {daily_registrations}")  # Debug log
        
        # Create date range from start_date to end_date
        date_range = [(start_date + timedelta(days=x)).date() for x in range(days + 1)]
        
        # Convert query results to dict for easy lookup
        registration_dict = {str(reg.date): reg.count for reg in daily_registrations}
        
        dates = [str(date) for date in date_range]
        counts = [registration_dict.get(date, 0) for date in dates]
        
        return {
            "dates": dates,
            "counts": counts
        }
    except Exception as e:
        print(f"Error in registration trends: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch registration trends: {str(e)}"
        )


@router.get("/analytics/active-users")
async def get_active_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get active users metrics"""
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "inactive_users": total_users - active_users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/role-distribution")
async def get_role_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get user role distribution metrics"""
    try:
        roles = db.query(User.role, func.count(User.id)).group_by(User.role).all()
        return {
            "roles": [role for role, _ in roles],
            "counts": [count for _, count in roles]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/login-activity")
async def get_login_activity(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily login counts
        daily_logins = (
            db.query(
                func.date(LoginActivity.timestamp).label('date'),
                func.count(LoginActivity.id).label('count')
            )
            .filter(LoginActivity.timestamp >= start_date)
            .filter(LoginActivity.success == True)
            .group_by(func.date(LoginActivity.timestamp))
            .order_by(func.date(LoginActivity.timestamp))
            .all()
        )
        
        # Create date range
        date_range = [(start_date + timedelta(days=x)).date() for x in range(days + 1)]
        
        # Convert to dict for lookup
        login_dict = {str(login.date): login.count for login in daily_logins}
        
        dates = [str(date) for date in date_range]
        counts = [login_dict.get(date, 0) for date in dates]
        
        # Get total successful and failed attempts
        total_success = db.query(LoginActivity).filter(
            LoginActivity.success == True,
            LoginActivity.timestamp >= start_date
        ).count()
        
        total_failed = db.query(LoginActivity).filter(
            LoginActivity.success == False,
            LoginActivity.timestamp >= start_date
        ).count()
        
        # Enhanced failure metrics
        recent_failures = (
            db.query(LoginActivity)
            .filter(
                LoginActivity.success == False,
                LoginActivity.timestamp >= start_date
            )
            .order_by(LoginActivity.timestamp.desc())
            .limit(5)
            .all()
        )

        # Get IP-based statistics
        ip_failures = (
            db.query(
                LoginActivity.ip_address,
                func.count(LoginActivity.id).label('attempts')
            )
            .filter(
                LoginActivity.success == False,
                LoginActivity.timestamp >= start_date
            )
            .group_by(LoginActivity.ip_address)
            .having(func.count(LoginActivity.id) > 3)  # IPs with multiple failures
            .all()
        )

        return {
            "dates": dates,
            "counts": counts,
            "total_success": total_success,
            "total_failed": total_failed,
            "recent_failures": [
                {
                    "timestamp": str(failure.timestamp),
                    "ip_address": failure.ip_address,
                    "user_id": failure.user_id
                } for failure in recent_failures
            ],
            "suspicious_ips": [
                {
                    "ip": ip,
                    "failure_count": count
                } for ip, count in ip_failures
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))