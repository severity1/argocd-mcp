"""Application management tools for ArgoCD MCP"""

from typing import Dict, Any, List, Optional, Union, cast
import logging
from api.client import make_api_request
from models.applications import (
    application_to_api_format,
    api_format_to_application,
    Application,
    ApplicationSource,
    ApplicationDestination,
    ApplicationSyncPolicy,
)

logger = logging.getLogger("argocd_mcp")


async def list_applications(
    project: str = "",
    name: str = "",
    repo: str = "",
    namespace: str = "",
    refresh: str = "",
) -> Dict[str, Any]:
    """
    List applications in ArgoCD with filtering options

    Args:
        project: Filter applications by project name
        name: Filter applications by name
        repo: Filter applications by repository URL
        namespace: Filter applications by namespace
        refresh: Forces application reconciliation if set to 'hard' or 'normal'

    Returns:
        List of applications with pagination information
    """
    params = {}

    if project:
        params["project"] = project

    if name:
        params["name"] = name

    if repo:
        params["repo"] = repo

    if namespace:
        params["appNamespace"] = namespace

    if refresh in ["hard", "normal"]:
        params["refresh"] = refresh

    success, data = await make_api_request("applications", params=params)

    if not success:
        return {"error": data.get("error", "Failed to retrieve applications")}

    return data


async def get_application_details(
    name: str, project: str = "", refresh: str = "", namespace: str = ""
) -> Dict[str, Any]:
    """
    Get details for a specific application

    Args:
        name: The application name (required)
        project: The project name (optional filter)
        refresh: Forces application reconciliation if set to 'hard' or 'normal'
        namespace: Filter by application namespace

    Returns:
        Application details
    """
    params = {}

    if project:
        params["project"] = project

    if refresh in ["hard", "normal"]:
        params["refresh"] = refresh

    if namespace:
        params["appNamespace"] = namespace

    success, data = await make_api_request(f"applications/{name}", params=params)

    if success:
        return data
    else:
        return {
            "error": data.get(
                "error", f"Failed to get details for application '{name}'"
            )
        }


async def create_application(
    name: str,
    project: str,
    repo_url: str,
    path: str,
    dest_server: str,
    dest_namespace: str,
    revision: str = "HEAD",
    automated_sync: bool = False,
    prune: bool = False,
    self_heal: bool = False,
    namespace: str = "",
    validate: bool = True,
    upsert: bool = False,
) -> Dict[str, Any]:
    """
    Create a new application in ArgoCD

    Args:
        name: The name of the application (required)
        project: The project name (required)
        repo_url: The Git repository URL (required)
        path: Path within the repository (required)
        dest_server: Destination K8s API server URL (required)
        dest_namespace: Destination namespace (required)
        revision: Git revision (default: HEAD)
        automated_sync: Enable automated sync (default: False)
        prune: Auto-prune resources (default: False)
        self_heal: Enable self-healing (default: False)
        namespace: Application namespace
        validate: Whether to validate the application before creation
        upsert: Whether to update the application if it already exists

    Returns:
        The created application details
    """
    # Create application structure
    app = Application(
        name=name,
        project=project,
        source=ApplicationSource(
            repo_url=repo_url, path=path, target_revision=revision
        ),
        destination=ApplicationDestination(
            server=dest_server, namespace=dest_namespace
        ),
    )

    # Add sync policy if automated sync is enabled
    if automated_sync:
        app.sync_policy = ApplicationSyncPolicy(
            automated=True, prune=prune, self_heal=self_heal
        )

    if namespace:
        app.namespace = namespace

    # Convert to API format
    data = application_to_api_format(app)

    # Add query parameters
    params = {}
    if validate:
        params["validate"] = "true"
    if upsert:
        params["upsert"] = "true"

    success, response = await make_api_request(
        "applications", method="POST", data=data, params=params
    )

    if success:
        logger.info(f"Application '{name}' created successfully")
        return response
    else:
        logger.error(f"Failed to create application '{name}': {response.get('error')}")
        return {"error": response.get("error", "Failed to create application")}


async def update_application(
    name: str,
    project: Optional[str] = None,
    repo_url: Optional[str] = None,
    path: Optional[str] = None,
    dest_server: Optional[str] = None,
    dest_namespace: Optional[str] = None,
    revision: Optional[str] = None,
    automated_sync: Optional[bool] = None,
    prune: Optional[bool] = None,
    self_heal: Optional[bool] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """
    Update an existing application in ArgoCD

    Args:
        name: The application name to update (required)
        project: New project name (optional)
        repo_url: New Git repository URL (optional)
        path: New path within the repository (optional)
        dest_server: New destination K8s API server URL (optional)
        dest_namespace: New destination namespace (optional)
        revision: New Git revision (optional)
        automated_sync: Enable/disable automated sync (optional)
        prune: Enable/disable auto-pruning resources (optional)
        self_heal: Enable/disable self-healing (optional)
        validate: Whether to validate the application

    Returns:
        The updated application details
    """
    # First get the current application details
    success, app_data = await make_api_request(f"applications/{name}")
    if not success:
        return {
            "error": app_data.get(
                "error", f"Failed to get current application details for '{name}'"
            )
        }

    # Update fields only if provided
    if project:
        app_data["spec"]["project"] = project

    if repo_url or path or revision:
        # Update source fields
        source = app_data["spec"].get("source", {})
        if repo_url:
            source["repoURL"] = repo_url
        if path:
            source["path"] = path
        if revision:
            source["targetRevision"] = revision
        app_data["spec"]["source"] = source

    if dest_server or dest_namespace:
        # Update destination fields
        destination = app_data["spec"].get("destination", {})
        if dest_server:
            destination["server"] = dest_server
        if dest_namespace:
            destination["namespace"] = dest_namespace
        app_data["spec"]["destination"] = destination

    # Update sync policy if any of those parameters are provided
    if automated_sync is not None or prune is not None or self_heal is not None:
        sync_policy = app_data["spec"].get("syncPolicy", {})
        automated = (
            sync_policy.get("automated", {}) if "automated" in sync_policy else None
        )

        # Create automated section if it doesn't exist but should
        if automated_sync is True and automated is None:
            automated = {}
            sync_policy["automated"] = automated

        # Remove automated section if it exists but should not
        elif automated_sync is False and automated is not None:
            del sync_policy["automated"]

        # Update automated settings
        if automated is not None:
            if prune is not None:
                automated["prune"] = prune
            if self_heal is not None:
                automated["selfHeal"] = self_heal

        app_data["spec"]["syncPolicy"] = sync_policy

    # Add query parameters
    params = {}
    if validate:
        params["validate"] = "true"

    # Update the application
    success, response = await make_api_request(
        f"applications/{name}", method="PUT", data=app_data, params=params
    )

    if success:
        logger.info(f"Application '{name}' updated successfully")
        return response
    else:
        logger.error(f"Failed to update application '{name}': {response.get('error')}")
        return {
            "error": response.get("error", f"Failed to update application '{name}'")
        }


async def delete_application(
    name: str, cascade: bool = True, propagation_policy: str = "", namespace: str = ""
) -> Dict[str, Any]:
    """
    Delete an application from ArgoCD

    Args:
        name: The name of the application to delete (required)
        cascade: Whether to delete application resources as well (default: True)
        propagation_policy: The propagation policy ("foreground", "background", or "orphan")
        namespace: The application namespace (optional)

    Returns:
        Success message or error details
    """
    params = {"cascade": str(cascade).lower()}

    if propagation_policy and propagation_policy in [
        "foreground",
        "background",
        "orphan",
    ]:
        params["propagationPolicy"] = propagation_policy

    if namespace:
        params["appNamespace"] = namespace

    success, data = await make_api_request(
        f"applications/{name}", method="DELETE", params=params
    )

    if success:
        logger.info(f"Application '{name}' deleted successfully (cascade: {cascade})")
        return {
            "status": "success",
            "message": f"Application '{name}' deleted successfully",
            "details": data,
        }
    else:
        logger.error(f"Failed to delete application '{name}': {data.get('error')}")
        return {
            "error": data.get("error", f"Failed to delete application '{name}'"),
            "details": data,
        }


async def sync_application(
    name: str,
    revision: str = "",
    prune: bool = False,
    dry_run: bool = False,
    strategy: str = "",
    resources: Optional[List[Dict[str, str]]] = None,
    namespace: str = "",
) -> Dict[str, Any]:
    """
    Sync an application in ArgoCD

    Args:
        name: The name of the application to sync (required)
        revision: Git revision to sync to (optional)
        prune: Whether to prune resources (default: False)
        dry_run: Whether to perform a dry run (default: False)
        strategy: Sync strategy ("apply" or "hook")
        resources: List of resources to sync (optional)
        namespace: The application namespace (optional)

    Returns:
        Sync result details
    """
    data = {"name": name, "prune": prune, "dryRun": dry_run}

    if revision:
        data["revision"] = revision

    if strategy and strategy in ["apply", "hook"]:
        data["strategy"] = {"hook": {}} if strategy == "hook" else {"apply": {}}

    if resources:
        data["resources"] = resources

    params = {}
    if namespace:
        params["appNamespace"] = namespace

    success, response = await make_api_request(
        f"applications/{name}/sync", method="POST", data=data, params=params
    )

    if success:
        logger.info(f"Application '{name}' sync initiated")
        return response
    else:
        logger.error(f"Failed to sync application '{name}': {response.get('error')}")
        return {"error": response.get("error", f"Failed to sync application '{name}'")}
