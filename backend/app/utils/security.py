import secrets
import string
from passlib.context import CryptContext
from .token import generate_verification_token  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

    hash_password = get_password_hash
    verify_password = verify_password  

# Add this function at the end of the file
def create_verification_token() -> str:
    """Backwards-compatibility alias for token generation"""
    return generate_verification_token()

# Add to existing security.py functions
def generate_temp_password(length: int = 12) -> str:
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))