// frontend/src/api.js

const API_BASE_URL = process.env.REACT_APP_API_BASE || "http://localhost:18000";
console.log("API base URL:", API_BASE_URL); // ✅ Debug log to confirm the API base

// Store and retrieve tokens
export const storeTokens = (accessToken, refreshToken) => {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
};

export const getAccessToken = () => localStorage.getItem("access_token");
export const getRefreshToken = () => localStorage.getItem("refresh_token");

export const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// Wrapper for authenticated fetch
export const apiFetch = async (endpoint, method = "GET", body = null) => {
  const token = getAccessToken();
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    if (res.status === 401) {
      throw new Error("Unauthorized: Invalid or expired token.");
    }

    return await res.json();
  } catch (err) {
    console.error(`[apiFetch error] ${err}`);
    throw err;
  }
};

// Specific API calls

export const getAccounts = async () => {
  return await apiFetch("/api/accounts");
};

export const getTransactions = async () => {
  return await apiFetch("/api/transactions");
};

export const evaluateLoan = async (encryptedPayload) => {
  return await apiFetch("/api/loan/evaluate", "POST", {
    encrypted_payload: encryptedPayload,
  });
};
