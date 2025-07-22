from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from app.models.user import UserCreate, User
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)
from app.database import db
from app.config import settings
from bson import ObjectId
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    try:
        # Log the registration attempt
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Check if user already exists
        existing_user = await db.get_db().users.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"Registration failed: Email {user.email} already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please use a different email or try logging in."
            )

        # Create new user
        user_dict = user.model_dump()
        user_dict["password"] = get_password_hash(user_dict["password"])
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        # Log the user data (excluding password)
        logger.info(f"Creating user with data: {user_dict.get('name')}, {user_dict.get('email')}")
        
        try:
            result = await db.get_db().users.insert_one(user_dict)
            if not result.inserted_id:
                logger.error("Failed to insert user: No inserted_id returned")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
        except Exception as db_error:
            logger.error(f"Database error during user creation: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating user"
            )
        
        # Verify user was created
        created_user = await db.get_db().users.find_one({"_id": result.inserted_id})
        if not created_user:
            logger.error(f"User creation verification failed: User not found after creation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but not found"
            )
            
        logger.info(f"Successfully created user with email: {user.email}")
        # Convert ObjectId to string for Pydantic model
        created_user["_id"] = str(created_user["_id"])
        return User(**created_user)
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise he
    except Exception as e:
        # Log the full error traceback
        logger.error(f"Unexpected error during registration: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.info(f"Login attempt for email: {form_data.username}")
        
        # Authenticate user
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Login failed: Invalid credentials for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for email: {form_data.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "theme_preference": user.theme_preference
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/clear-db")
async def clear_database():
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in development mode"
        )
    
    try:
        result = await db.get_db().users.delete_many({})
        logger.info(f"Cleared database: {result.deleted_count} users deleted")
        return {"message": f"Database cleared. {result.deleted_count} users deleted."}
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear database"
        )

@router.post("/update-theme", response_model=User)
async def update_theme_preference(theme: str = Query(...), current_user: User = Depends(get_current_user)):
    try:
        if theme not in ["light", "dark"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Theme must be either 'light' or 'dark'"
            )
        
        # Update the user's theme preference
        result = await db.get_db().users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"theme_preference": theme, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update theme preference"
            )
            
        # Get the updated user
        updated_user = await db.get_db().users.find_one({"_id": ObjectId(current_user.id)})
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Convert ObjectId to string for Pydantic model
        updated_user["_id"] = str(updated_user["_id"])
        return User(**updated_user)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating theme preference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating theme preference"
        )
