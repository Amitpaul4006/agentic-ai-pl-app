const API_URL = '/api/transactions/';

document.addEventListener('DOMContentLoaded', () => {
    fetchTransactions();

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
