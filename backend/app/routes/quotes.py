from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from app.models.quote import Quote, QuoteCreate, QuoteUpdate
from app.database import db
from bson import ObjectId
from app.auth import get_current_user, get_current_user_optional
from app.models.user import User
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quotes", tags=["quotes"])

@router.get("/", response_model=List[Quote])
async def get_quotes(current_user: Optional[User] = Depends(get_current_user_optional)):
    # Get all quotes and calculate their score (likes - dislikes)
    quotes = await db.get_db().quotes.find().to_list(length=100)
    
    # Sort quotes by score (likes - dislikes) in descending order
    # First sort by the difference between likes and dislikes
    # For quotes with the same difference, sort by total likes
    quotes.sort(key=lambda x: (
        x.get("likes", 0) - x.get("dislikes", 0),  # Primary sort by net score
        x.get("likes", 0)  # Secondary sort by total likes
    ), reverse=True)
    
    # Get user's liked and disliked quotes if user is authenticated
    user_liked_quotes = []
    user_disliked_quotes = []
    if current_user:
        user = await db.get_db().users.find_one({"_id": ObjectId(current_user.id)})
        user_liked_quotes = user.get("liked_quotes", [])
        user_disliked_quotes = user.get("disliked_quotes", [])
    
    # Populate user information and liked/disliked status for each quote
    for quote in quotes:
        if quote.get("user_id"):
            user = await db.get_db().users.find_one({"_id": ObjectId(quote["user_id"])})
            if user:
                quote["user_name"] = user.get("name", "Unknown User")
        # Add is_liked and is_disliked fields (only if user is authenticated)
        quote["is_liked"] = str(quote["_id"]) in user_liked_quotes if current_user else False
        quote["is_disliked"] = str(quote["_id"]) in user_disliked_quotes if current_user else False
    
    return quotes

@router.get("/search")
async def search_quotes(
    author: Optional[str] = None,
    quote: Optional[str] = None,
    tags: Optional[str] = None
):
    query = {}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if quote:
        query["quote"] = {"$regex": quote, "$options": "i"}
    if tags:
        query["tags"] = {"$regex": tags, "$options": "i"}

    quotes = await db.get_db().quotes.find(query).to_list(length=None)
    
    # Populate user information for each quote
    for quote in quotes:
        if quote.get("user_id"):
            user = await db.get_db().users.find_one({"_id": ObjectId(quote["user_id"])})
            if user:
                quote["user_name"] = user.get("name", "Unknown User")
    
    return quotes

@router.get("/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")
    
    quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

@router.post("/", response_model=Quote)
async def create_quote(quote: QuoteCreate, current_user: User = Depends(get_current_user)):
    try:
        quote_dict = quote.model_dump()
        quote_dict["user_id"] = str(current_user.id)
        quote_dict["user_name"] = current_user.name
        result = await db.get_db().quotes.insert_one(quote_dict)
        created_quote = await db.get_db().quotes.find_one({"_id": result.inserted_id})
        if not created_quote:
            raise HTTPException(status_code=500, detail="Failed to create quote")
        return created_quote
    except Exception as e:
        logger.error(f"Error creating quote: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create quote")

@router.patch("/{quote_id}", response_model=Quote)
async def update_quote(
    quote_id: str,
    quote: QuoteUpdate,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")
    
    existing_quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    if not existing_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    if str(existing_quote["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this quote")
    
    update_data = quote.model_dump(exclude_unset=True)
    await db.get_db().quotes.update_one(
        {"_id": ObjectId(quote_id)},
        {"$set": update_data}
    )
    
    updated_quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    return updated_quote

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")
    
    existing_quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    if not existing_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    if str(existing_quote["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this quote")
    
    await db.get_db().quotes.delete_one({"_id": ObjectId(quote_id)})
    return None

@router.post("/{quote_id}/likes/up")
async def like_quote(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    # Check if user has already liked this quote
    quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Get user's liked quotes
    user = await db.get_db().users.find_one({"_id": ObjectId(current_user.id)})
    liked_quotes = user.get("liked_quotes", [])
    disliked_quotes = user.get("disliked_quotes", [])

    if str(quote_id) in liked_quotes:
        # User has already liked this quote, remove the like
        await db.get_db().quotes.update_one(
            {"_id": ObjectId(quote_id)},
            {"$inc": {"likes": -1}}
        )
        # Remove quote from user's liked quotes
        await db.get_db().users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"liked_quotes": str(quote_id)}}
        )
        return {"message": "Like removed successfully"}
    else:
        # User hasn't liked this quote, add the like
        await db.get_db().quotes.update_one(
            {"_id": ObjectId(quote_id)},
            {"$inc": {"likes": 1}}
        )
        # Add quote to user's liked quotes
        await db.get_db().users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$addToSet": {"liked_quotes": str(quote_id)}}
        )

        # If user had disliked this quote, remove the dislike
        if str(quote_id) in disliked_quotes:
            await db.get_db().quotes.update_one(
                {"_id": ObjectId(quote_id)},
                {"$inc": {"dislikes": -1}}
            )
            await db.get_db().users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$pull": {"disliked_quotes": str(quote_id)}}
            )

        return {"message": "Like added successfully"}

@router.post("/{quote_id}/likes/down")
async def unlike_quote(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    result = await db.get_db().quotes.update_one(
        {"_id": ObjectId(quote_id)},
        {"$inc": {"likes": -1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return {"message": "Like removed successfully"}

@router.post("/{quote_id}/dislike/up")
async def dislike_quote(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    # Check if user has already disliked this quote
    quote = await db.get_db().quotes.find_one({"_id": ObjectId(quote_id)})
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Get user's disliked quotes
    user = await db.get_db().users.find_one({"_id": ObjectId(current_user.id)})
    disliked_quotes = user.get("disliked_quotes", [])
    liked_quotes = user.get("liked_quotes", [])

    if str(quote_id) in disliked_quotes:
        # User has already disliked this quote, remove the dislike
        await db.get_db().quotes.update_one(
            {"_id": ObjectId(quote_id)},
            {"$inc": {"dislikes": -1}}
        )
        # Remove quote from user's disliked quotes
        await db.get_db().users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"disliked_quotes": str(quote_id)}}
        )
        return {"message": "Dislike removed successfully"}
    else:
        # User hasn't disliked this quote, add the dislike
        await db.get_db().quotes.update_one(
            {"_id": ObjectId(quote_id)},
            {"$inc": {"dislikes": 1}}
        )
        # Add quote to user's disliked quotes
        await db.get_db().users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$addToSet": {"disliked_quotes": str(quote_id)}}
        )

        # If user had liked this quote, remove the like
        if str(quote_id) in liked_quotes:
            await db.get_db().quotes.update_one(
                {"_id": ObjectId(quote_id)},
                {"$inc": {"likes": -1}}
            )
            await db.get_db().users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$pull": {"liked_quotes": str(quote_id)}}
            )

        return {"message": "Dislike added successfully"}

@router.post("/{quote_id}/dislike/down")
async def remove_dislike(quote_id: str):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    result = await db.get_db().quotes.update_one(
        {"_id": ObjectId(quote_id)},
        {"$inc": {"dislikes": -1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return {"message": "Dislike removed successfully"}

@router.get("/{quote_id}/reactions")
async def get_quote_reactions(quote_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(quote_id):
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    # Get all users who liked the quote
    liked_users = await db.get_db().users.find(
        {"liked_quotes": str(quote_id)},
        {"name": 1, "_id": 0}
    ).to_list(length=None)

    # Get all users who disliked the quote
    disliked_users = await db.get_db().users.find(
        {"disliked_quotes": str(quote_id)},
        {"name": 1, "_id": 0}
    ).to_list(length=None)

    return {
        "likes": [user["name"] for user in liked_users],
        "dislikes": [user["name"] for user in disliked_users]
    }
