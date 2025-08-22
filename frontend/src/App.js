import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

// Simple token storage
const getToken = () => localStorage.getItem('fintrust_token');
const setToken = (token) => localStorage.setItem('fintrust_token', token);
const removeToken = () => localStorage.removeItem('fintrust_token');

// API client with auth
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedUserId, setSelectedUserId] = useState('user-001');

  // Available users for demo
  const availableUsers = [
    { id: 'user-001', name: 'John Doe', email: 'john@example.com' },
    { id: 'user-002', name: 'Jane Smith', email: 'jane@example.com' },
    { id: 'user-003', name: 'Bob Wilson', email: 'bob@example.com' },
    { id: 'admin', name: 'Administrator', email: 'admin@fintrust.com' }
  ];

  // Login function
  const login = async (userId) => {
    try {
      setLoading(true);
      setError('');

      const response = await axios.post(`${API_BASE}/auth/login?user_id=${userId}`);
      const { access_token, user: userData } = response.data;

      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);

      // Load user data
      await loadUserData();

    } catch (err) {
      setError(`Login failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load user accounts and transactions
  const loadUserData = async () => {
    try {
      setLoading(true);

      // Load accounts
      const accountsResponse = await api.get('/api/v1/accounts');
      setAccounts(accountsResponse.data.accounts || []);

      // Load transactions  
      const transactionsResponse = await api.get('/api/v1/transactions');
      setTransactions(transactionsResponse.data.transactions || []);

    } catch (err) {
      setError(`Failed to load data: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = () => {
    removeToken();
    setIsAuthenticated(false);
    setUser(null);
    setAccounts([]);
    setTransactions([]);
  };

  // Check if already logged in on load
  useEffect(() => {
    const token = getToken();
    if (token) {
      // Verify token is still valid by making a test request
      api.get('/health')
        .then(() => {
          setIsAuthenticated(true);
          loadUserData();
        })
        .catch(() => {
          removeToken();
        });
    }
  }, []);

  // Login screen
  if (!isAuthenticated) {
    return (
      <div className="App">
        <div className="login-container">
          <h1>🏦 FinTrust Gateway</h1>
          <p>Secure Financial API Platform</p>

          <div className="login-form">
            <h3>Development Login</h3>
            <select 
              value={selectedUserId} 
              onChange={(e) => setSelectedUserId(e.target.value)}
              disabled={loading}
            >
              {availableUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </option>
              ))}
            </select>

            <button 
              onClick={() => login(selectedUserId)}
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>

            {error && <div className="error">{error}</div>}
          </div>
        </div>
      </div>
    );
  }

  // Main dashboard
  return (
    <div className="App">
      <header className="App-header">
        <h1>🏦 FinTrust Gateway</h1>
        <div className="user-info">
          <span>Welcome, {user?.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      <main className="dashboard">
        {/* Accounts Section */}
        <section className="accounts-section">
          <h2>💳 Your Accounts</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div className="accounts-grid">
              {accounts.length > 0 ? (
                accounts.map(account => (
                  <div key={account.id} className="account-card">
                    <h3>{account.account_type}</h3>
                    <p className="balance">${account.balance.toFixed(2)}</p>
                    <small>ID: {account.id}</small>
                  </div>
                ))
              ) : (
                <p>No accounts found</p>
              )}
            </div>
          )}
        </section>

        {/* Transactions Section */}
        <section className="transactions-section">
          <h2>📊 Recent Transactions</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div className="transactions-list">
              {transactions.length > 0 ? (
                transactions.slice(0, 10).map(transaction => (
                  <div key={transaction.id} className="transaction-item">
                    <div className="transaction-info">
                      <strong>{transaction.merchant || 'Transfer'}</strong>
                      <small>{transaction.description}</small>
                    </div>
                    <div className={`amount ${transaction.amount < 0 ? 'debit' : 'credit'}`}>
                      {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                    </div>
                    <div className="date">
                      {new Date(transaction.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                ))
              ) : (
                <p>No transactions found</p>
              )}
            </div>
          )}
        </section>

        {/* Quick Actions */}
        <section className="actions-section">
          <h2>⚡ Quick Actions</h2>
          <button onClick={loadUserData} disabled={loading}>
            🔄 Refresh Data
          </button>
          <button onClick={() => window.open(`${API_BASE}/docs`, '_blank')}>
            📖 API Documentation
          </button>
        </section>
      </main>
    </div>
  );
}

export default App;