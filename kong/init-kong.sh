#!/bin/bash

# Wait for Kong Admin API to be ready
until curl -s http://localhost:8001/status; do
  echo "Waiting for Kong to be ready..."
  sleep 3
done

echo "✅ Kong Admin API is up. Initializing routes..."

# ------------------------------------------------------------------------------
# SERVICE: FinTrust Backend (FastAPI)
# ------------------------------------------------------------------------------

curl -i -X PUT http://localhost:8001/services/backend \
  --data "url=http://backend:8000"

curl -i -X PUT http://localhost:8001/routes/backend-route \
  --data "paths[]=/api" \
  --data "service.name=backend"

# ------------------------------------------------------------------------------
# OAUTH2 Plugin (Protect /api using OAuth2 from Keycloak)
# ------------------------------------------------------------------------------

# Enable OAuth2 plugin on backend service
curl -i -X POST http://localhost:8001/services/backend/plugins \
  --data "name=oauth2" \
  --data "config.enable_authorization_code=true" \
  --data "config.global_credentials=true" \
  --data "config.scopes=read_accounts,read_transactions,loan_evaluation" \
  --data "config.mandatory_scope=true" \
  --data "config.provision_key=provision123" \
  --data "config.token_expiration=3600"

# Register Kong as an OAuth2 client with itself
curl -i -X POST http://localhost:8001/oauth2_credentials \
  --data "name=kong-client" \
  --data "client_id=kong-client" \
  --data "client_secret=kong-secret" \
  --data "redirect_uris[]=http://localhost:8000/test/cb" \
  --data "provision_key=provision123" \
  --data "service_id=$(curl -s http://localhost:8001/services/backend | jq -r '.id')"

# ------------------------------------------------------------------------------
# Test Route for OAuth2 callback
# ------------------------------------------------------------------------------

curl -i -X PUT http://localhost:8001/routes/test-callback \
  --data "paths[]=/test/cb" \
  --data "strip_path=false" \
  --data "service.name=backend"

echo "✅ Kong Gateway initialized with routes and OAuth2 plugin."
