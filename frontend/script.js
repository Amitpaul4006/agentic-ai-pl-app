const API_URL = '/api/transactions/';
const CHAT_API_URL = '/api/chat';

document.addEventListener('DOMContentLoaded', () => {
    fetchTransactions();
    initializeChat();

    const form = document.getElementById('transaction-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const description = document.getElementById('description').value;
        const amount = parseFloat(document.getElementById('amount').value);
        const type = document.getElementById('type').value;

        const transaction = { description, amount, type };

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(transaction),
            });

            if (response.ok) {
                form.reset();
                fetchTransactions();
            } else {
                console.error('Error adding transaction');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});

// Chat Widget Functions
function initializeChat() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatClose = document.getElementById('chat-close');
    const chatSend = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const chatWidget = document.getElementById('chat-widget');

    // Toggle chat widget
    chatToggle.addEventListener('click', () => {
        chatWidget.classList.toggle('active');
        if (chatWidget.classList.contains('active')) {
            chatInput.focus();
        }
    });

    // Close chat widget
    chatClose.addEventListener('click', () => {
        chatWidget.classList.remove('active');
    });

    // Send message on button click
    chatSend.addEventListener('click', () => {
        sendChatMessage();
    });

    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatMessage('user', message);
    chatInput.value = '';
    chatInput.focus();

    try {
        const response = await fetch(CHAT_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (response.ok) {
            const data = await response.json();
            addChatMessage('bot', data.response);
            
            // Refresh transactions in case they were modified
            fetchTransactions();
        } else {
            console.error('Error getting chat response');
            addChatMessage('bot', '❌ Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        addChatMessage('bot', '❌ Connection error. Please try again.');
    }
}

function addChatMessage(sender, text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const messageText = document.createElement('p');
    messageText.textContent = text;
    
    messageDiv.appendChild(messageText);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Refresh transactions after bot responds
    if (sender === 'bot') {
        fetchTransactions();
    }
}

async function fetchTransactions() {
    try {
        const response = await fetch(API_URL);
        const transactions = await response.json();
        updateTable(transactions);
        updateSummary(transactions);
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

function updateTable(transactions) {
    const tbody = document.getElementById('transactions-body');
    tbody.innerHTML = '';

    transactions.forEach(t => {
        const row = document.createElement('tr');
        const dateStr = new Date(t.date).toLocaleDateString();
        
        row.innerHTML = `
            <td>${dateStr}</td>
            <td>${t.description}</td>
            <td class="${t.type}">${t.type.charAt(0).toUpperCase() + t.type.slice(1)}</td>
            <td class="${t.type}">$${t.amount.toFixed(2)}</td>
            <td><button class="delete-btn" onclick="deleteTransaction(${t.id})">Delete</button></td>
        `;
        tbody.appendChild(row);
    });
}

function updateSummary(transactions) {
    let income = 0;
    let expenses = 0;

    transactions.forEach(t => {
        if (t.type === 'income') {
            income += t.amount;
        } else {
            expenses += t.amount;
        }
    });

    const net = income - expenses;

    document.getElementById('total-income').innerText = `$${income.toFixed(2)}`;
    document.getElementById('total-expenses').innerText = `$${expenses.toFixed(2)}`;
    
    const netEl = document.getElementById('net-profit');
    netEl.innerText = `$${net.toFixed(2)}`;
    netEl.className = net >= 0 ? 'income' : 'expense';
}

async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            fetchTransactions();
        } else {
            console.error('Error deleting transaction');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
