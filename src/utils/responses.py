from typing import Any, Optional, Dict
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """Standard success response format."""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str = "Error",
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Dict[str, Any]:
    """Standard error response format."""
    response = {
        "success": False,
        "message": message
    }
    if errors:
        response["errors"] = errors
    return response


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success"
) -> Dict[str, Any]:
    """Standard paginated response format."""
    return {
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }
