from pydantic import BaseModel
from pydantic import validator

# Base schema with common attributes
class ItemBase(BaseModel):
    name: str
    description: str = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Item cannot be empty,please provide a valid item name')
        return v

# Schema for creating a new item
class ItemCreate(ItemBase):
    pass

# Schema for reading/returning an item (includes id)
class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True
        