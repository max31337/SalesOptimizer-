from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
# Corrected import to include AdminInviteCreate and UserCreate
from app.schemas.user import AdminInviteCreate, UserCreate, UserUpdate
from app.middleware.admin import admin_required
from app.services.user_service import UserService # Added missing import for UserService
from app.services.admin_service import AdminService
from app.services.email import email_service # Ensure email_service is imported correctly
from app.utils.security import generate_temp_password # Added missing import
from app.utils.token import create_verification_token # Added missing import
from sqlalchemy.exc import IntegrityError # Import IntegrityError
# Remove unused debugging imports if desired
# from sqlalchemy.orm.session import object_session
# from sqlalchemy import inspect
import logging
# import traceback # Keep if detailed tracebacks are needed in logs

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG) # Configure logging centrally

router = APIRouter()

# Remove /admin prefix from individual routes since it's handled by the parent router
@router.get("/users/list", response_model=Dict[str, Any])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """List users with pagination, search, and filtering"""
    admin_service = AdminService(db)
    return admin_service.list_users(skip, limit, search, role, is_active)

@router.get("/users/details/{user_id}", response_model=Dict[str, Any])
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Get a single user by ID"""
    admin_service = AdminService(db)
    return admin_service.get_user_details(user_id)

@router.put("/users/update/{user_id}", response_model=Dict[str, str])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Update user details"""
    admin_service = AdminService(db)
    return admin_service.update_user(user_id, user_update, current_user.id)

@router.delete("/users/deactivate/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Soft delete a user by setting is_active to False"""
    admin_service = AdminService(db)
    return admin_service.deactivate_user(user_id, current_user.id)

@router.post("/verify-user/{user_id}")
async def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Verify a user account"""
    admin_service = AdminService(db)
    return admin_service.verify_user(user_id)


@router.post("/invite/", tags=["admin"])
async def invite_user(
    user_data: AdminInviteCreate, # Now defined due to corrected import
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    logger.debug(f"--- Starting invite_user for email: {user_data.email} ---")
    logger.debug(f"Route handler session ID: {id(db)}")
    try:
        user_service = UserService(db) # Pass the session, though the service might use its own UoW
        temp_password = generate_temp_password() # Generate the temporary password

        user_create_data = UserCreate( # Now defined due to corrected import
            **user_data.model_dump(),
            password=temp_password,
            confirm_password=temp_password,
            is_active=False
        )
        logger.debug(f"Prepared UserCreate data: {user_create_data.model_dump(exclude={'password', 'confirm_password'})}")

        # Store the email from the input data, not the potentially detached object
        user_email_to_verify = user_data.email

        try:
            logger.debug("Calling user_service.create_user...")
            # Assume create_user commits internally and returns the object (possibly detached)
            # We don't need to use the returned object directly if it might be detached.
            _ = user_service.create_user(user_create_data) # Assign to _ to indicate we don't use the return value here
            logger.debug(f"User creation initiated by service for email: {user_email_to_verify}")

        except IntegrityError as ie: # Catch duplicate email error from the service layer commit
             db.rollback() # Ensure rollback in the route's session just in case
             logger.error(f"❌ IntegrityError during user creation for {user_email_to_verify}: {str(ie)}")
             # Check if it's a unique constraint violation (This part already handles existing emails)
             if "unique constraint" in str(ie).lower() or "duplicate key" in str(ie).lower():
                 raise HTTPException(status_code=409, detail=f"User with email {user_email_to_verify} already exists.")
             else:
                 raise HTTPException(status_code=500, detail="Database integrity error during user creation.")
        except Exception as create_error:
            # Log the original error from the service layer
            logger.error(f"Error during user_service.create_user for {user_email_to_verify}: {create_error}", exc_info=True)
            # Raise a generic 500 error for the client
            raise HTTPException(status_code=500, detail="Failed to create user due to an internal error.")

        # --- Re-fetch the user using the route's session (db) and the known email ---
        logger.debug(f"Re-fetching user with email {user_email_to_verify} using route session {id(db)}")
        user = db.query(User).filter(User.email == user_email_to_verify).first()

        if not user:
             logger.error(f"Failed to re-fetch user with email {user_email_to_verify} after creation attempt.")
             # This case implies create_user might have failed silently or rolled back without raising IntegrityError
             raise HTTPException(status_code=404, detail="User creation might have failed or user could not be found immediately.")

        logger.debug(f"Successfully re-fetched user. User ID: {user.id}")
        # --- End Re-fetch ---

        logger.debug(f"Attempting to access user.email ({user.email}) for token creation.")
        invite_token = create_verification_token(email=user.email)
        logger.debug(f"Invite token created successfully.")

        # Pass the temp_password to the email service function
        await email_service.send_invite_email(
            email=user.email,
            token=invite_token,
            temp_password=temp_password # Added missing argument
        )
        logger.debug(f"Email sending initiated for {user.email}.")

        # No db.commit() or db.refresh() needed here, as create_user handled the commit,
        # and we re-fetched the user into the current session.

        logger.debug(f"--- Successfully processed invite for {user.email} ---")
        return {"message": "Invitation sent successfully"}

    # Keep existing general exception handlers
    except HTTPException as http_exc:
        # Log and re-raise HTTPExceptions (like the 409 or 404 above)
        logger.warning(f"HTTPException caught: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # db.rollback() # Rollback might be needed if an error occurs after re-fetch but before return
        logger.error(f"❌ Unexpected Error in invite_user for email {user_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")