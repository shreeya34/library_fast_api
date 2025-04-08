from fastapi.responses import JSONResponse
from typing import Dict, Any


def json_response(content: Dict[str, Any], status_code: int) -> JSONResponse:
    """
    Helper function to create a JSON response with content and a status code.

    :param content: The content to send in the response, typically a dictionary.
    :param status_code: The HTTP status code to return.
    :return: FastAPI JSONResponse.
    """
    return JSONResponse(content=content, status_code=status_code)
