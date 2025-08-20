// frontend/src/AuditLogger.js

import React, { useState } from "react";
import { getAccessToken } from "./api";

const AUDIT_API = process.env.REACT_APP_AUDIT_URL || "http://localhost:8000/api/audit";

const AuditLogger = () => {
  const [logMessage, setLogMessage] = useState("");
  const [response, setResponse] = useState(null);

  const sendAuditLog = async () => {
    const token = getAccessToken();
    if (!token) {
      alert("Access token not found. Please login.");
      return;
    }

    try {
      const res = await fetch(AUDIT_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          action: "manual_audit_log",
          details: logMessage,
        }),
      });

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Failed to send audit log:", err);
      setResponse({ error: "Failed to send log" });
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>📋 Audit Logger</h2>
      <textarea
        rows={4}
        style={{ width: "100%" }}
        placeholder="Enter audit log message"
        value={logMessage}
        onChange={(e) => setLogMessage(e.target.value)}
      />
      <button onClick={sendAuditLog} style={{ marginTop: "1rem" }}>
        Send Audit Log
      </button>

      {response && (
        <div style={{ marginTop: "1rem", color: response.error ? "red" : "green" }}>
          <strong>Server Response:</strong>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default AuditLogger;
