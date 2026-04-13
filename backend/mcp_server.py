from mcp.server.fastmcp import FastMCP
from sqlalchemy.orm import Session
from .app import models, database
from datetime import datetime
import os

# Initialize FastMCP server
mcp = FastMCP("PL-App-Manager")

def get_db_session():
    return database.SessionLocal()

@mcp.tool()
def add_transaction(description: str, amount: float, type: str, date: str = None) -> str:
    """Add a new transaction to the database.
    type must be 'income' or 'expense'. 
    date format should be YYYY-MM-DD (defaults to now)."""
    db = get_db_session()
    try:
        transaction_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        new_transaction = models.Transaction(
            description=description,
            amount=amount,
            type=type.lower(),
            date=transaction_date
        )
        db.add(new_transaction)
        db.commit()
        return f"Successfully added {type}: {description} for ${amount:.2f}"
    except Exception as e:
        return f"Error adding transaction: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def get_summary() -> str:
    """Calculate and return total income, total expenses, and net profit/loss."""
    db = get_db_session()
    try:
        transactions = db.query(models.Transaction).all()
        income = sum(t.amount for t in transactions if t.type == 'income')
        expenses = sum(t.amount for t in transactions if t.type == 'expense')
        net = income - expenses
        return (f"Summary:\n"
                f"Total Income: ${income:.2f}\n"
                f"Total Expenses: ${expenses:.2f}\n"
                f"Net Profit/Loss: ${net:.2f}")
    finally:
        db.close()

@mcp.tool()
def get_transactions() -> str:
    """List all transactions currently in the database."""
    db = get_db_session()
    try:
        transactions = db.query(models.Transaction).all()
        if not transactions:
            return "No transactions found."
        
        output = "Transactions:\n"
        for t in transactions:
            output += f"[{t.id}] {t.date.strftime('%Y-%m-%d')} | {t.type.upper()} | {t.description}: ${t.amount:.2f}\n"
        return output
    finally:
        db.close()

@mcp.tool()
def delete_transaction(transaction_id: int) -> str:
    """Delete a transaction by ID and return the updated summary."""
    db = get_db_session()
    try:
        transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
        if not transaction:
            return f"Transaction with ID {transaction_id} not found."
        
        db.delete(transaction)
        db.commit()
        
        summary = get_summary()
        return f"Deleted transaction {transaction_id}.\n\nUpdated {summary}"
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
