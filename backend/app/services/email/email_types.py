from enum import Enum

class EmailType(str, Enum):
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    INVITATION = "invitation"