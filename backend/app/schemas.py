from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: str

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    title: str
    amount: float
    tags: Optional[List[str]] = []


class ExpenseCreate(ExpenseBase):
    timestamp: Optional[datetime] = None
    type: Optional[str] = "expense"


class Expense(ExpenseBase):
    id: str
    timestamp: datetime
    tags: List[Tag]

    class Config:
        from_attributes = True
