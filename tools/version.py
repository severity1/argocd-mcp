"""Version service tools for ArgoCD MCP"""

from typing import Dict, Any
from api.client import make_api_request


async def get_version() -> Dict[str, Any]:
    """
    Version returns version information of the API server using api/version

    This endpoint returns version details of the ArgoCD API server including
    Git commit, version, build date, compiler information, and more.

    Returns:
        Version information of the ArgoCD API server
    """
    # Note: This endpoint uses a different base path ('/api/version' instead of '/api/v1/...')
    # We need to modify the path to point to just 'version' since the client adds '/api/v1/'
    success, data = await make_api_request("../version")

    if success:
        # Return the full version response
        return data
    else:
        # Return a properly structured error dictionary
        return {
            "error": data.get("error", "Failed to retrieve ArgoCD version information")
        }
