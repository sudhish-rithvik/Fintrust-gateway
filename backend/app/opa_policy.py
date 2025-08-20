import os
import requests
from fastapi import HTTPException

# Default OPA URL (adjust for Docker if needed)
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181")
POLICY_PATH = "/v1/data/fintrust/allow"

def check_access(user_id: str, action: str, resource: str, roles: list = []):
    """
    Calls OPA to check whether the user is allowed to perform an action on a resource.
    """
    input_payload = {
        "input": {
            "user": user_id,
            "action": action,
            "resource": resource,
            "roles": roles
        }
    }

    try:
        response = requests.post(f"{OPA_URL}{POLICY_PATH}", json=input_payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="OPA policy decision failed")

        decision = response.json()
        if not decision.get("result", False):
            raise HTTPException(status_code=403, detail="Access denied by policy")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"OPA server error: {str(e)}")
