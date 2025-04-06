# auth_utils.py
from fastapi import Request, HTTPException
from typing import Optional


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extracts the Bearer token from the request headers.
    """
    auth_header = request.headers.get("authorization") or request.headers.get(
        "Authorization"
    )

    if not auth_header or "Bearer " not in auth_header:
        raise HTTPException(
            status_code=401, detail="No token received or incorrect format!"
        )

    return auth_header
