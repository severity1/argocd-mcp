"""Session service tools for ArgoCD MCP"""

import os
from typing import Dict, Any
from api.client import make_api_request


async def get_user_info() -> Dict[str, Any]:
    """
    Get the current user's info via session/userinfo

    This endpoint returns information about the currently logged-in user,
    including permissions and groups.

    Returns:
        User information from ArgoCD
    """
    # Use the session userinfo endpoint with global setting from client.py
    success, data = await make_api_request("session/userinfo")

    if success:
        # Return the full user info response
        return data
    else:
        # Make sure to return a properly structured error dictionary
        return {"error": data.get("error", "Failed to retrieve user information")}
