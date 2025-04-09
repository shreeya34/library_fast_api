import time
from typing import Dict
from fastapi import HTTPException, Header
import jwt
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()


JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def token_response(token: str):
    return {"access_token": token}


def signJWT(name: str, user_id: str, is_admin: bool = False) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "name": name,
        "is_admin": is_admin,
        "expires": time.time() + 86400,
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(jwt_token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Check if the token is expired
        if decoded_token["expires"] >= time.time():
            return decoded_token
        return None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_current_user(authorization: str = Header(...)) -> dict:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token scheme")

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        return {
            "username": payload.get("name"),
            "is_admin": payload.get("is_admin"),
            "admin_id": payload.get("user_id"),
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
