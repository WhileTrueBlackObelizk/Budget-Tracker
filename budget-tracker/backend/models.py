"""
Database models for the Budget Tracker.
"""

from sqlalchemy import Column, Integer, String, Float, Date, Computed
from sqlalchemy.sql import func
from database import Base


class Transaction(Base):
    """Represents a single income or expense entry."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    type = Column(String(10), nullable=False, index=True)  # "income" | "expense"
    date = Column(Date, nullable=False, server_default=func.current_date())
    note = Column(String(255), nullable=True, default="")

    # Computed helper columns for easy filtering
    month = Column(Integer, nullable=False, default=0)
    year = Column(Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.date:
            self.month = self.date.month
            self.year = self.date.year

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, type='{self.type}', "
            f"amount={self.amount}, category='{self.category}')>"
        )
