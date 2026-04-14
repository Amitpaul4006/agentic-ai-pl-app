import google.generativeai as genai
from typing import Optional
import os
import json
from datetime import datetime
from . import models, database

# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ChatService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
    def get_db_session(self):
        return database.SessionLocal()
    
    def add_transaction(self, description: str, amount: float, type: str, date: str = None) -> str:
        """Add a new transaction to the database."""
        db = self.get_db_session()
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
            return f"✓ Added {type.capitalize()}: {description} for ${amount:.2f}"
        except Exception as e:
            return f"✗ Error adding transaction: {str(e)}"
        finally:
            db.close()
    
    def get_summary(self) -> str:
        """Calculate and return total income, total expenses, and net profit/loss."""
        db = self.get_db_session()
        try:
            transactions = db.query(models.Transaction).all()
            income = sum(t.amount for t in transactions if t.type == 'income')
            expenses = sum(t.amount for t in transactions if t.type == 'expense')
            net = income - expenses
            return (f"📊 Summary:\n"
                    f"💰 Total Income: ${income:.2f}\n"
                    f"📉 Total Expenses: ${expenses:.2f}\n"
                    f"📈 Net Profit/Loss: ${net:.2f}")
        finally:
            db.close()
    
    def get_transactions(self) -> str:
        """List all transactions currently in the database."""
        db = self.get_db_session()
        try:
            transactions = db.query(models.Transaction).all()
            if not transactions:
                return "No transactions found."
            
            output = "📋 All Transactions:\n"
            for t in transactions:
                icon = "📥" if t.type == "income" else "📤"
                output += f"{icon} [{t.id}] {t.date.strftime('%Y-%m-%d')} | {t.type.upper()} | {t.description}: ${t.amount:.2f}\n"
            return output
        finally:
            db.close()
    
    def delete_transaction(self, transaction_id: int) -> str:
        """Delete a transaction by ID."""
        db = self.get_db_session()
        try:
            transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
            if not transaction:
                return f"✗ Transaction with ID {transaction_id} not found."
            
            db.delete(transaction)
            db.commit()
            return f"✓ Deleted transaction {transaction_id}.\n\n{self.get_summary()}"
        finally:
            db.close()
    
    def process_chat(self, user_message: str) -> str:
        """Process user message with Gemini and call appropriate tools."""
        
        # Build tools definition for Gemini
        tools_definition = """
You have access to the following functions to manage P&L transactions:

1. add_transaction(description, amount, type, date=None)
   - Adds a new transaction
   - type: "income" or "expense"
   - date: optional, format "YYYY-MM-DD"
   - Returns: confirmation message

2. get_summary()
   - Returns total income, expenses, and net profit/loss
   - No parameters needed

3. get_transactions()
   - Returns list of all transactions
   - No parameters needed

4. delete_transaction(transaction_id)
   - Deletes a transaction by ID
   - Returns: confirmation and updated summary

When the user asks to:
- Add/record a transaction: Use add_transaction
- See summary/P&L: Use get_summary
- List all transactions: Use get_transactions
- Delete/remove a transaction: Use delete_transaction

Always respond in a friendly, conversational manner. Extract dates, amounts, and descriptions from user input intelligently.
If the user's request is ambiguous, ask for clarification.
"""

        # Create a conversation with Gemini
        try:
            # Add context about available tools
            full_prompt = f"""{tools_definition}

User: {user_message}

Based on the user's request, decide which function(s) to call and what parameters to use.
Respond with EITHER:
1. A JSON object with "action" and "params" keys if you need to call a function
2. A friendly message if no function is needed or for clarifications

For function calls, respond ONLY with valid JSON like:
{{"action": "add_transaction", "params": {{"description": "...", "amount": 100.0, "type": "income"}}}}

{{"action": "get_summary", "params": {{}}}}

{{"action": "get_transactions", "params": {{}}}}

{{"action": "delete_transaction", "params": {{"transaction_id": 1}}}}

For non-function responses, respond with plain text."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            
            response_text = response.text.strip()
            
            # Try to parse as JSON for function calls
            try:
                if response_text.startswith("{") and response_text.endswith("}"):
                    data = json.loads(response_text)
                    action = data.get("action")
                    params = data.get("params", {})
                    
                    # Execute the appropriate function
                    if action == "add_transaction":
                        return self.add_transaction(**params)
                    elif action == "get_summary":
                        return self.get_summary()
                    elif action == "get_transactions":
                        return self.get_transactions()
                    elif action == "delete_transaction":
                        return self.delete_transaction(**params)
                    else:
                        return response_text
                else:
                    return response_text
            except json.JSONDecodeError:
                # Not JSON, return as regular response
                return response_text
                
        except Exception as e:
            return f"✗ Error processing request: {str(e)}"

# Create a singleton instance
chat_service = ChatService()
