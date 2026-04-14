import google.generativeai as genai
from typing import Optional
import os
import json
import re
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
        
        # Extract intent and parameters more directly
        try:
            prompt = f"""You are a financial assistant for managing P&L transactions.

The user said: "{user_message}"

You have these functions available:
1. add_transaction(description, amount, type, date) - Add income or expense. type is "income" or "expense". date format is YYYY-MM-DD.
2. get_summary() - Get income, expenses, and net P&L
3. get_transactions() - List all transactions
4. delete_transaction(transaction_id) - Delete a transaction by its ID

Based on what the user wants, respond with ONLY a JSON object (no other text):
- If adding transaction: {{"action": "add_transaction", "params": {{"description": "...", "amount": 123.45, "type": "income", "date": "2026-04-14"}}}}
- If getting summary: {{"action": "get_summary", "params": {{}}}}
- If listing transactions: {{"action": "get_transactions", "params": {{}}}}
- If deleting: {{"action": "delete_transaction", "params": {{"transaction_id": 5}}}}
- If unsure or clarification needed: {{"action": "clarify", "params": {{"message": "..."}}}}

IMPORTANT: Respond ONLY with valid JSON, nothing else."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more consistent JSON
                    max_output_tokens=500,
                )
            )
            
            response_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                # Find JSON in response (in case there's extra text)
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                else:
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
                elif action == "clarify":
                    return params.get("message", "I didn't understand. Please try again.")
                else:
                    return f"Unknown action: {action}. Please try again."
                    
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to understand the intent from the text
                lower_msg = user_message.lower()
                
                if "summary" in lower_msg or "total" in lower_msg or "profit" in lower_msg or "loss" in lower_msg:
                    return self.get_summary()
                elif "list" in lower_msg or "show" in lower_msg or "all" in lower_msg or "transaction" in lower_msg:
                    return self.get_transactions()
                elif "delete" in lower_msg or "remove" in lower_msg:
                    # Try to extract transaction ID
                    match = re.search(r'\d+', user_message)
                    if match:
                        transaction_id = int(match.group())
                        return self.delete_transaction(transaction_id)
                    else:
                        return "🤔 Could you please specify which transaction ID to delete?"
                elif "add" in lower_msg or "income" in lower_msg or "expense" in lower_msg:
                    return "📝 I need more details: Please specify the amount, description, and whether it's income or expense."
                else:
                    return f"🤔 I'm not sure what you're asking. Here's what I can help with:\n- Add a transaction\n- Show summary\n- List all transactions\n- Delete a transaction\n\nFull response: {response_text}"
                
        except Exception as e:
            return f"✗ Error processing request: {str(e)}"

# Create a singleton instance
chat_service = ChatService()
