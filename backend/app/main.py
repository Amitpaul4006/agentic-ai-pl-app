from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .chat_service import chat_service

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.post("/api/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/api/transactions/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions

@app.delete("/api/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.delete_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

# Chat endpoint for natural language interactions
@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat(chat_message: schemas.ChatMessage):
    """Process natural language message and interact with P&L tools via Gemini."""
    response = chat_service.process_chat(chat_message.message)
    return schemas.ChatResponse(response=response)

# Serve frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("../frontend/index.html")
