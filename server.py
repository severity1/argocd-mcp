#!/usr/bin/env python3
"""
ArgoCD MCP Server

This server provides a Model Context Protocol (MCP) interface to the ArgoCD API,
allowing large language models and AI assistants to manage ArgoCD resources.
"""
import logging
import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import tools and models
from api.client import DEFAULT_API_URL
import tools.session as session
import tools.applications as applications
import tools.settings as settings
import tools.version as version

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create server instance
mcp = FastMCP("ArgoCD MCP Server")

# Register session service tool - only provides user info via userinfo endpoint
mcp.tool()(session.get_user_info)

# Register settings service tools
mcp.tool()(settings.get_settings)
mcp.tool()(settings.get_plugins)

# Register version service tool
mcp.tool()(version.get_version)

# Register application tools
mcp.tool()(applications.list_applications)
mcp.tool()(applications.get_application_details)
mcp.tool()(applications.create_application)
mcp.tool()(applications.update_application)
mcp.tool()(applications.delete_application)
mcp.tool()(applications.sync_application)

# Start server when run directly
if __name__ == "__main__":
    mcp.run()
