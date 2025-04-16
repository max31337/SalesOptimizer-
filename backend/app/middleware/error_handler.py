from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
# Update the existing import line
from app.core.exceptions import (
    BaseAppException, 
    ValidationError,
    AuthenticationError,  # Add missing import
    AuthorizationError,
    DatabaseError
)
from typing import Union, Dict, Any
import traceback
import logging

logger = logging.getLogger(__name__)

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except ValidationError as exc:
        return create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            detail=str(exc)
        )
    except AuthenticationError as exc:
        return create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
            detail=str(exc)
        )
    except BaseAppException as exc:
        return create_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            detail=exc.detail,
            data=exc.data
        )
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {str(exc)}\n{traceback.format_exc()}")
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            detail="A database error occurred"
        )
    except Exception as exc:
        logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            detail="An unexpected error occurred"
        )

def create_error_response(
    status_code: int,
    error_code: str,
    detail: str,
    data: Dict[str, Any] = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": detail,
                "data": data or {}
            }
        }
    )