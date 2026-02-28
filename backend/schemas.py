"""
Pydantic schemas for request validation and response serialisation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
import datetime
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class CategoryType(str, Enum):
    groceries = "Lebensmittel"
    rent = "Miete"
    leisure = "Freizeit"
    transport = "Transport"
    salary = "Gehalt"
    other = "Sonstiges"


# ── Request schemas ───────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount (positive number)")
    category: str = Field(..., min_length=1, max_length=50, description="Category name")
    type: TransactionType = Field(..., description="'income' or 'expense'")
    date: datetime.date | None = Field(None, description="Transaction date (defaults to today)")
    note: str | None = Field("", max_length=255, description="Optional note")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "amount": 45.90,
                    "category": "Lebensmittel",
                    "type": "expense",
                    "date": "2025-03-15",
                    "note": "Wocheneinkauf REWE",
                }
            ]
        }
    }


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    type: TransactionType | None = None
    date: datetime.date | None = None
    note: str | None = Field(None, max_length=255)


# ── Response schemas ──────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: int
    amount: float
    category: str
    type: str
    date: datetime.date
    note: Optional[str]

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    category: str
    total: float


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int
    categories: list[CategorySummary] = []
