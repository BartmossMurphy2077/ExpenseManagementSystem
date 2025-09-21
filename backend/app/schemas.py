from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: str
    class Config:
        orm_mode = True

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
        orm_mode = True
