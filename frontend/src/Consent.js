// frontend/src/Consent.js

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAccessToken, apiFetch } from "./api";

const requestedScopes = [
  { name: "accounts", description: "View your account balances and types" },
  { name: "transactions", description: "Access your transaction history" },
  { name: "loan", description: "Allow encrypted loan eligibility check" }
];

const Consent = () => {
  const [consentGiven, setConsentGiven] = useState({});
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleCheckboxChange = (scopeName) => {
    setConsentGiven((prev) => ({
      ...prev,
      [scopeName]: !prev[scopeName]
    }));
  };

  const handleSubmit = async () => {
    console.log("🔘 Submit button clicked");

    const token = getAccessToken();
    console.log("🔐 Access token:", token);

    if (!token) {
      setError("Access token missing. Please log in.");
      return;
    }

    const grantedScopes = Object.keys(consentGiven).filter(scope => consentGiven[scope]);
    console.log("✅ Granted scopes:", grantedScopes);

    if (grantedScopes.length === 0) {
      setError("You must select at least one scope to continue.");
      return;
    }

    try {
      console.log("📤 Sending audit to /api/audit");

      await apiFetch("/api/audit", "POST", {
        action: "consent_granted",
        details: `User granted consent for: ${grantedScopes.join(", ")}`
      });

      console.log("✅ Audit submitted successfully. Navigating to /loan");
      navigate("/loan");
    } catch (err) {
      console.error("❌ Audit submission failed:", err);
      setError("Failed to submit consent. Please try again.");
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>🛡️ Data Consent Dashboard</h2>
      <p>Please review and approve the data scopes you wish to share:</p>

      <ul style={{ listStyleType: "none", padding: 0 }}>
        {requestedScopes.map((scope) => (
          <li key={scope.name} style={{ marginBottom: "1rem" }}>
            <label>
              <input
                type="checkbox"
                checked={consentGiven[scope.name] || false}
                onChange={() => handleCheckboxChange(scope.name)}
              />
              <strong> {scope.name}</strong>: {scope.description}
            </label>
          </li>
        ))}
      </ul>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <button onClick={handleSubmit} style={{ marginTop: "1rem" }}>
        Submit Consent
      </button>
    </div>
  );
};

export default Consent;
