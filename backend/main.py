"""
Budget Tracker API – FastAPI Backend
=====================================
REST API for managing personal income and expense transactions.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
import os

from .database import engine, get_db, Base
from .models import Transaction
from .schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    SummaryResponse,
    CategorySummary,
)

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Budget Tracker API",
    description="A personal budget tracker to record and analyse income & expenses.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow frontend (dev & prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the frontend index.html at the root URL."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Budget Tracker API is running. Visit /docs for the API documentation."}


# ── Transactions ──────────────────────────────────────────────────────────

@app.get("/transactions", response_model=list[TransactionResponse], tags=["Transactions"])
def get_transactions(
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type (income/expense)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db),
):
    """Retrieve all transactions, optionally filtered by category, type, month or year."""
    query = db.query(Transaction)

    if category:
        query = query.filter(Transaction.category == category)
    if type:
        query = query.filter(Transaction.type == type)
    if month:
        query = query.filter(Transaction.month == month)
    if year:
        query = query.filter(Transaction.year == year)

    return query.order_by(Transaction.date.desc()).all()


@app.post("/transactions", response_model=TransactionResponse, status_code=201, tags=["Transactions"])
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new income or expense transaction."""
    transaction = Transaction(
        amount=payload.amount,
        category=payload.category,
        type=payload.type,
        date=payload.date or date.today(),
        note=payload.note,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Retrieve a single transaction by ID."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.put("/transactions/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    """Update an existing transaction."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@app.delete("/transactions/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction by ID."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()


# ── Summary ───────────────────────────────────────────────────────────────

@app.get("/summary", response_model=SummaryResponse, tags=["Summary"])
def get_summary(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
    db: Session = Depends(get_db),
):
    """
    Get a financial summary with total income, expenses, balance and
    a breakdown by category. Optionally filter by month/year.
    """
    query = db.query(Transaction)

    if month:
        query = query.filter(Transaction.month == month)
    if year:
        query = query.filter(Transaction.year == year)

    transactions = query.all()

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")

    # Category breakdown (expenses only)
    category_map: dict[str, float] = {}
    for t in transactions:
        if t.type == "expense":
            category_map[t.category] = category_map.get(t.category, 0) + t.amount

    categories = [
        CategorySummary(category=cat, total=total)
        for cat, total in sorted(category_map.items(), key=lambda x: -x[1])
    ]

    return SummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(total_income - total_expenses, 2),
        transaction_count=len(transactions),
        categories=categories,
    )
