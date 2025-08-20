// frontend/src/Login.js

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { storeTokens } from "./api";

const KEYCLOAK_URL = process.env.REACT_APP_KEYCLOAK_URL || "http://localhost:8080";
const REALM = process.env.REACT_APP_KEYCLOAK_REALM || "fintrust";
const CLIENT_ID = process.env.REACT_APP_KEYCLOAK_CLIENT_ID || "frontend-client";
const REDIRECT_URI = process.env.REACT_APP_REDIRECT_URI || "http://localhost:3000/login";
const TOKEN_ENDPOINT = `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`;

function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      exchangeCodeForToken(code);
    }
  }, []);

  const redirectToKeycloak = () => {
    const authUrl = `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/auth?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=openid`;
    window.location.href = authUrl;
  };

  const exchangeCodeForToken = async (code) => {
    try {
      const body = new URLSearchParams();
      body.append("grant_type", "authorization_code");
      body.append("code", code);
      body.append("redirect_uri", REDIRECT_URI);
      body.append("client_id", CLIENT_ID);

      const response = await fetch(TOKEN_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body
      });

      const data = await response.json();

      if (data.access_token) {
        storeTokens(data.access_token, data.refresh_token);
        navigate("/consent");
      } else {
        console.error("Token exchange failed", data);
      }
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "3rem" }}>
      <h2>🔐 Login to FinTrust Gateway</h2>
      <p>To use our secure services, please authenticate with your identity provider.</p>
      <button onClick={redirectToKeycloak} style={{ padding: "0.75rem 2rem", fontSize: "1rem" }}>
        Login with Keycloak
      </button>
    </div>
  );
}

export default Login;
