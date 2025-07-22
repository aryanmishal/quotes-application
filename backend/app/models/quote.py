from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string"}

class QuoteBase(BaseModel):
    quote: str
    author: str
    tags: Optional[str] = None
    likes: int = 0
    dislikes: int = 0
    is_active: bool = True
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    is_liked: Optional[bool] = False
    is_disliked: Optional[bool] = False

class QuoteCreate(QuoteBase):
    pass

class QuoteUpdate(BaseModel):
    quote: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None

class Quote(QuoteBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True
