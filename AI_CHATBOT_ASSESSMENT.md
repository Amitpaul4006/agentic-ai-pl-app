# P&L App - AI Chatbot Assessment

## 📋 Project Overview

This document provides details about the AI-powered chatbot integration for the P&L (Profit & Loss) application. The chatbot uses natural language processing to allow users to manage transactions without manual form entry.

---

## 🤖 LLM Details

### Current Model in Use
**`gemini-2.5-flash`**
- ✅ Model Type: Google Gemini (Latest Flash)
- ✅ Cost: Free tier (20 requests/day), Pay-as-you-go for higher usage
- ✅ Latency: Very fast (~1-2 seconds)
- ✅ Context Understanding: Excellent at parsing natural language financial requests

### Alternative Models Available
Your API key supports these models which can be used as alternatives:

1. **`gemini-2.5-pro`**
   - More powerful reasoning for complex transactions
   - Slightly slower but more accurate
   - Same quota: 20 requests/day free, then paid

2. **`gemini-2.0-flash`**
   - Older version of flash model
   - Slightly faster, similar capability
   - Same quota: 20 requests/day free, then paid

3. **`gemini-flash-latest`** (Recommended alternative)
   - Always points to the latest flash version
   - Good balance of speed and accuracy
   - Same quota: 20 requests/day free, then paid

**Note:** All Google Gemini models on free tier have a **20 requests per day limit**. For production use, enable billing for unlimited requests (~$0.075 per 1M tokens).

---

## 🧪 Testing Prompts

Use the following prompts to test the chatbot functionality. Enter them in the chat widget on the deployed app:

### 1. **Add Income Transaction**
```
Add an income transaction of $5000 for "Consulting Project" dated 2026-04-14
```
**Expected:** New income appears in table, Total Income increases

---

### 2. **Add Expense Transaction**
```
Record an expense of $1200 for "Office Supplies"
```
**Expected:** New expense appears in table, Total Expenses increases

---

### 3. **Add Transaction (Natural Language)**
```
I made $3500 from product sales yesterday
```
**Expected:** Income transaction automatically added, Summary updates

---

### 4. **Get Summary/P&L**
```
What's my current P&L summary?
```
or
```
Show me my profit and loss
```
**Expected:** Bot displays Total Income, Total Expenses, and Net Profit/Loss

---

### 5. **List All Transactions**
```
List all my transactions
```
or
```
Show me all transactions
```
**Expected:** Formatted list with Date, Description, Type, Amount for all transactions

---

### 6. **Delete Transaction**
```
Delete transaction 2
```
**Expected:** Specified transaction removed, Summary updates automatically

---

### 7. **Edge Case - Invalid Delete**
```
Delete transaction 999
```
**Expected:** Error message: "Transaction not found"

---

### 8. **Edge Case - Ambiguous Request**
```
Add $500
```
**Expected:** Bot asks for clarification on type and description

---

## 📁 Project Links

### GitHub Repository
```
https://github.com/Amitpaul4006/agentic-ai-pl-app
```
**Contains:**
- FastAPI backend with chat endpoint
- Gemini AI integration via `google-generativeai`
- SQLAlchemy ORM with PostgreSQL
- Custom MCP server with 4 tools
- Plain HTML/CSS/JS frontend with chat widget

### Deployed Application
```
https://pl-app-backend.onrender.com/
```
**Live Demo:** Click the 💬 button to open the AI Assistant chat widget

---

## 🔧 Technical Stack

- **Backend:** FastAPI + Python
- **Database:** PostgreSQL (Render)
- **AI:** Google Gemini API
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **MCP Tools:** 
  - `add_transaction()` - Create income/expense
  - `get_summary()` - View P&L totals
  - `get_transactions()` - List all transactions
  - `delete_transaction()` - Remove transaction

---

## 💡 Architecture

1. **User** → Types natural language request in chat widget
2. **Frontend** → Sends message to `/api/chat` endpoint
3. **Backend** → Routes to ChatService
4. **Gemini AI** → Parses intent and generates JSON action
5. **Action Execution** → Calls appropriate MCP tool (add/delete/get)
6. **Database** → Transaction created/deleted
7. **Response** → Formatted message returned to user
8. **Dashboard** → Auto-updates with new data

---

## 🎯 Key Features

✅ Natural language transaction management  
✅ Real-time P&L calculation  
✅ Intelligent prompt fallback (works even if LLM response is unexpected)  
✅ Mobile-responsive chat widget  
✅ Seamless database integration  
✅ Error handling and validation  

---

**Created:** April 14, 2026  
**Assessment:** Autodesk - Senior Software Engineer + AI Automation
