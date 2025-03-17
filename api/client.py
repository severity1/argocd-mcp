"""ArgoCD API client

This module provides a client for interacting with the ArgoCD API.
It handles authentication, request formatting, and response parsing.
"""

import os
import logging
from typing import Optional, Dict, Tuple, Any
from urllib.parse import urljoin
import httpx

# Constants
# Default URL to use if no environment variable is set
ARGOCD_API_URL_DEFAULT = "http://localhost:8080/api/v1"

# Store default token from environment variable
# Security note: API tokens are sensitive data and should never be logged or exposed
DEFAULT_TOKEN = os.getenv("ARGOCD_TOKEN")
DEFAULT_API_URL = os.getenv("ARGOCD_API_URL", ARGOCD_API_URL_DEFAULT)

# SSL verification setting (set to False to disable SSL verification)
# This is useful for development environments or when using self-signed certificates
VERIFY_SSL = os.getenv("ARGOCD_VERIFY_SSL", "true").lower() != "false"

# Log token presence but not the token itself
if DEFAULT_TOKEN:
    logging.info("Default token provided (masked for security)")


async def make_api_request(
    path: str,
    method: str = "GET",
    token: Optional[str] = None,
    api_url: Optional[str] = None,
    params: Dict[str, Any] = {},
    data: Dict[str, Any] = {},
    timeout: int = 30,
    verify_ssl: Optional[bool] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Make a request to the ArgoCD API

    Args:
        path: API path to request (without base URL)
        method: HTTP method (default: GET)
        token: API token (defaults to DEFAULT_TOKEN)
        api_url: ArgoCD API URL (defaults to DEFAULT_API_URL)
        params: Query parameters for the request (optional)
        data: JSON data for POST/PATCH requests (optional)
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certs (default: global setting)

    Returns:
        Tuple of (success, data) where data is either the response JSON or an error dict
    """
    if not token:
        token = DEFAULT_TOKEN

    if not token:
        return (
            False,
            {
                "error": "Token is required. Please set the ARGOCD_TOKEN environment variable."
            },
        )

    if not api_url:
        api_url = DEFAULT_API_URL

    # Use the provided verify_ssl value or fall back to the global setting
    ssl_verify = VERIFY_SSL if verify_ssl is None else verify_ssl

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout, verify=ssl_verify) as client:
            url = f"{api_url}/{path}"

            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(
                    url, headers=headers, params=params, json=data
                )
            elif method == "PUT":
                response = await client.put(
                    url, headers=headers, params=params, json=data
                )
            elif method == "PATCH":
                response = await client.patch(
                    url, headers=headers, params=params, json=data
                )
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                return (False, {"error": f"Unsupported method: {method}"})

            # Handle different success response codes
            if response.status_code in [200, 201, 202, 204]:
                if response.status_code == 204:  # No content
                    return (True, {"status": "success"})
                try:
                    return (True, response.json())
                except ValueError:
                    return (True, {"status": "success", "raw_response": response.text})
            else:
                error_message = f"API request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    # ArgoCD sometimes returns detailed error information
                    if "error" in error_data:
                        error_message = f"{error_message} - {error_data['error']}"
                    return (False, {"error": error_message, "details": error_data})
                except ValueError:
                    # Try to get text response if JSON parsing fails
                    error_text = response.text[:200] if response.text else ""
                    return (False, {"error": f"{error_message} - {error_text}"})
    except httpx.TimeoutException:
        return (False, {"error": f"Request timed out after {timeout} seconds"})
    except httpx.RequestError as e:
        error_message = str(e)
        return (False, {"error": f"Request error: {error_message}"})
    except Exception as e:
        # Ensure no sensitive data is included in error messages
        error_message = str(e)
        if token and token in error_message:
            error_message = error_message.replace(token, "[REDACTED]")
        return (False, {"error": f"Request error: {error_message}"})
