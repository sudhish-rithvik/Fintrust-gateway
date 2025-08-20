// frontend/src/App.js

import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";

import Login from "./Login";
import Consent from "./Consent";
import LoanResult from "./LoanResult";
import AuditLogger from "./AuditLogger";
import { getAccessToken } from "./api";

const PrivateRoute = ({ children }) => {
  const token = getAccessToken();
  return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <div className="App">
        <h1 style={{ textAlign: "center", marginTop: "1rem" }}>🔐 FinTrust Gateway</h1>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/consent"
            element={
              <PrivateRoute>
                <Consent />
              </PrivateRoute>
            }
          />
          <Route
            path="/loan"
            element={
              <PrivateRoute>
                <LoanResult />
              </PrivateRoute>
            }
          />
          <Route
            path="/audit"
            element={
              <PrivateRoute>
                <AuditLogger />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
