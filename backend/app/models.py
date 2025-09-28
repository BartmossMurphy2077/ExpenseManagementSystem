from sqlalchemy import Column, String, Float, Date, Table, ForeignKey  # change DateTime -> Date
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import date  # import date instead of datetime

Base = declarative_base()

# Many-to-many relationship stays the same
expense_tag_table = Table(
    "expense_tags",
    Base.metadata,
    Column("expense_id", String, ForeignKey("expenses.id")),
    Column("tag_id", String, ForeignKey("tags.id"))
)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(Date, default=date.today)  # store only date
    type = Column(String, default="expense")  # expense or inflow
    tags = relationship("Tag", secondary=expense_tag_table, back_populates="expenses")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    expenses = relationship("Expense", secondary=expense_tag_table, back_populates="tags")
