// frontend/src/LoanResult.js

import React, { useState } from "react";
import { evaluateLoan, apiFetch } from "./api";
import { getAccessToken } from "./api";

const LoanResult = () => {
  const [financialData, setFinancialData] = useState({ income: "", creditScore: "" });
  const [encryptedResult, setEncryptedResult] = useState("");
  const [loanDecision, setLoanDecision] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFinancialData({ ...financialData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    const { income, creditScore } = financialData;
    if (!income || !creditScore) {
      setError("Please fill in both income and credit score.");
      return;
    }

    try {
      setStatus("Encrypting and sending request...");

      // Dummy simulation: send fake encrypted payload
      const dummyEncryptedPayload = btoa(`${income}:${creditScore}`); // base64 placeholder

      const response = await evaluateLoan(dummyEncryptedPayload);

      if (response.error) {
        throw new Error(response.error);
      }

      setEncryptedResult(response.encrypted_loan_result);
      setStatus("Encrypted result received.");

      // 🔒 In production: decrypt with TenSEAL in WASM or locally
      const fakeDecryptedValue = 55500.0 + Math.random() * 5000; // simulate

      // Add differential privacy noise
      const epsilon = 1.0;
      const sensitivity = 1000.0;
      const noise = (Math.random() - 0.5) * 2 * sensitivity / epsilon;
      const finalScore = fakeDecryptedValue + noise;

      const decision = finalScore > 50000 ? "✅ Eligible" : "❌ Denied";
      setLoanDecision(decision);

      // Log event
      await apiFetch("/api/audit", "POST", {
        action: "loan_result_viewed",
        details: `Loan evaluated. Final score: ${finalScore.toFixed(2)} (${decision})`
      });

    } catch (err) {
      setError(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>💰 Loan Eligibility Check</h2>

      <div>
        <label>Monthly Income:</label>
        <input
          type="number"
          name="income"
          value={financialData.income}
          onChange={handleChange}
          placeholder="e.g. 55000"
        />
      </div>

      <div>
        <label>Credit Score:</label>
        <input
          type="number"
          name="creditScore"
          value={financialData.creditScore}
          onChange={handleChange}
          placeholder="e.g. 700"
        />
      </div>

      <button onClick={handleSubmit} style={{ marginTop: "1rem" }}>
        Submit Encrypted Request
      </button>

      {status && <p><strong>Status:</strong> {status}</p>}
      {encryptedResult && (
        <div>
          <h4>Encrypted Loan Score (base64):</h4>
          <textarea
            readOnly
            value={encryptedResult}
            style={{ width: "100%", height: "100px" }}
          />
        </div>
      )}
      {loanDecision && (
        <p style={{ fontSize: "1.2rem", marginTop: "1rem" }}>
          🧾 Final Decision: <strong>{loanDecision}</strong>
        </p>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default LoanResult;
