from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt
import logging
from datetime import datetime
from app.schemas.auth import TokenResponse
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import InvitedUserCompleteRegistration # Import the new schema
from app.utils.security import get_password_hash
from app.core.auth import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
# Update the logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True  # This will force the configuration even if logging was already configured
)

# Create a stream handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
console_handler.setFormatter(formatter)

# Get the logger and add the handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


@router.post("/register-invited/", response_model=TokenResponse)
# Use the new schema here instead of UserCreate
def register_invited_user(user_data: InvitedUserCompleteRegistration, db: Session = Depends(get_db)):
    """Register a new user who was invited by an admin"""
    logger.debug("="*50)
    logger.debug("Starting invited user registration process")
    logger.debug("="*50)

    # No longer need to log user_data.email as it's not in the new schema
    logger.debug(f"Received registration data:")
    logger.debug(f"Username: {user_data.username}")
    logger.debug(f"Token (first 20 chars): {user_data.invitation_token[:20]}...")

    # Token validation remains the same
    if not user_data.invitation_token:
        logger.error("❌ No invitation token provided in request")
        raise HTTPException(status_code=400, detail="Invitation token is required")

    try:
        logger.debug("-"*30)
        logger.debug("🔑 Attempting token verification")
        logger.debug(f"Algorithm: {settings.ALGORITHM}")
        logger.debug(f"Secret Key (first 10 chars): {settings.SECRET_KEY[:10]}...")
        
        payload = jwt.decode(
            user_data.invitation_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        logger.debug("✅ Token decoded successfully!")
        logger.debug(f"Payload: {payload}")

        email = payload.get("email") # Get email from token payload
        logger.debug(f"[9] Email extracted from token: {email}")

        if not email:
            logger.error("[10] No email found in token payload")
            raise HTTPException(status_code=400, detail="Invalid token format")

        # Find user by email from token
        logger.debug(f"[11] Searching for inactive user with email: {email}")
        user = db.query(User).filter(
            User.email == email,  # Use email from token
            User.is_active == False
        ).first()

        if not user:
            logger.error(f"[13] No inactive user found with email: {email}")
            raise HTTPException(status_code=404, detail="Invitation not found or already used")

        # Update user details using data from the new schema
        logger.debug("[14] Updating user details")
        user.username = user_data.username # Use username from payload
        user.password = get_password_hash(user_data.password) # Use password from payload
        user.is_active = True
        user.is_verified = True # Mark as verified upon completion

        logger.debug("[15] Committing changes to database")
        db.commit()
        db.refresh(user)

        # Generate access token
        access_token = create_access_token(data={"sub": email}) # Use email from token

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            role=user.role,
            is_verified=user.is_verified
        )

    except jwt.ExpiredSignatureError:
        logger.error("[ERROR] Token has expired")
        raise HTTPException(status_code=400, detail="Invitation token has expired")
    except jwt.JWTError as e:
        logger.error(f"[ERROR] JWT decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid invitation token")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {str(e)}")
        db.rollback() # Rollback in case of error during update/commit
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


# Add this new endpoint
@router.get("/check-invitation/{email}")  # Remove /auth prefix
async def check_invitation_status(email: str, db: Session = Depends(get_db)):
    """Debug endpoint to check user invitation status"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"status": "not_found"}
    return {
        "status": "found",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "has_password": bool(user.password)
    }


# Add this at the end of the file
@router.get("/register-invited/test")
async def test_route():
    """Test endpoint to verify routing"""
    logger.debug("Test endpoint hit successfully")
    return {
        "status": "success",
        "message": "Invited user registration route is working",
        "timestamp": datetime.now().isoformat()
    }