import time
from typing import Dict
from fastapi import HTTPException, Header
import jwt
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()


JWT_SECRET =  os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM =  os.getenv('JWT_ALGORITHM')

def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 1800 
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

def get_current_user(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    try:
        # Extract the token from the Authorization header
        token = authorization.split("Bearer ")[-1]
        
        decoded_token = decode_jwt(token)
        
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error: {str(e)}")
