"""Settings service tools for ArgoCD MCP"""

from typing import Dict, Any
from api.client import make_api_request


async def get_settings() -> Dict[str, Any]:
    """
    Get returns Argo CD settings using api/v1/settings

    This endpoint returns the ArgoCD server settings including
    configuration related to OIDC, Dex, UI customization, and plugins.

    Returns:
        ArgoCD server settings
    """
    success, data = await make_api_request("settings")

    if success:
        # Return the full settings response
        return data
    else:
        # Return a properly structured error dictionary
        return {"error": data.get("error", "Failed to retrieve ArgoCD settings")}


async def get_plugins() -> Dict[str, Any]:
    """
    Get returns Argo CD plugins using api/v1/settings/plugins

    This endpoint returns information about available plugins in ArgoCD.

    Returns:
        List of available plugins
    """
    success, data = await make_api_request("settings/plugins")

    if success:
        # Return the full plugins response
        return data
    else:
        # Return a properly structured error dictionary
        return {"error": data.get("error", "Failed to retrieve ArgoCD plugins")}
