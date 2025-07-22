from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.database import db
from app.config import settings
from bson import ObjectId
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str) -> Optional[User]:
    try:
        # Find user by email
        user_dict = await db.get_db().users.find_one({"email": email})
        if not user_dict:
            logger.warning(f"Authentication failed: User not found for email: {email}")
            return None
            
        # Convert ObjectId to string
        user_dict["_id"] = str(user_dict["_id"])
        
        # Verify password
        if not verify_password(password, user_dict["password"]):
            logger.warning(f"Authentication failed: Invalid password for email: {email}")
            return None
            
        logger.info(f"Authentication successful for email: {email}")
        return User(**user_dict)
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_dict = await db.get_db().users.find_one({"email": email})
    if user_dict is None:
        raise credentials_exception
        
    # Convert ObjectId to string
    user_dict["_id"] = str(user_dict["_id"])
    return User(**user_dict)

async def get_current_user_optional(token: str = Depends(oauth2_scheme_optional)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user_dict = await db.get_db().users.find_one({"email": email})
    if user_dict is None:
        return None
    user_dict["_id"] = str(user_dict["_id"])
    return User(**user_dict) 