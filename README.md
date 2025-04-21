# ArgoCD MCP Server

An MCP (Model Context Protocol) server that integrates with the ArgoCD API, enabling AI assistants and large language models to manage ArgoCD applications and resources through natural language interactions.

<a href="https://glama.ai/mcp/servers/@severity1/argocd-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@severity1/argocd-mcp/badge" alt="argocd-mcp MCP server" />
</a>

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Type Checking](https://img.shields.io/badge/type_checking-mypy-brightgreen)

## Features

- **Authentication & Session Management**:
  - User info retrieval from ArgoCD API
  - Token-based authentication with ArgoCD
  - Server settings and configuration access
  - Plugin information retrieval
  - Version information retrieval
- **Application Management**:
  - List and filter applications by project, name, namespace
  - Get detailed application information
  - Create, update, and delete applications
  - Sync applications with configurable options
- **Robust API Client**:
  - URL normalization and intelligent endpoint handling
  - Comprehensive error handling and detailed error messages
  - Configurable timeouts and SSL verification
  - Token security protection and masking
- **Developer Experience**:
  - Full static type checking with mypy
  - Detailed documentation and examples
  - Environment-based configuration

## Quick Start

### Setup

```bash
# Clone the repository
git clone https://github.com/severity1/argocd-mcp.git
cd argocd-mcp

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### Starting the Server

The server is configured via environment variables. Here are the available configuration options:

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `ARGOCD_TOKEN` | ArgoCD API token | None |
| `ARGOCD_API_URL` | ArgoCD API endpoint | https://argocd.example.com/api/v1 |
| `ARGOCD_VERIFY_SSL` | Verify SSL certificates | true |

You can start the server in several ways:

```bash
# Using MCP dev tools (provides debugging tools)
export ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
mcp dev server.py

# Using MCP run command
export ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
mcp run server.py

# Standard method
export ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
uv run server.py

# Setting multiple environment variables
export ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
export ARGOCD_API_URL=https://your-argocd-server.com:9000/api/v1
export ARGOCD_VERIFY_SSL=false  # Disable SSL verification for self-signed certs
uv run server.py

# Using a .env file
echo "ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
ARGOCD_API_URL=https://your-argocd-server.com:9000/api/v1
ARGOCD_VERIFY_SSL=false" > .env
uv run server.py

# Run in background
export ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN
uv run server.py > server.log 2>&1 & echo $! > server.pid
```

When the token is provided via environment variable, Claude can use it without you having to specify it in every command.

### Connecting with Claude

#### Using Claude Code CLI

```bash
# Add the MCP server
claude mcp add argocd-mcp "uv run $(pwd)/server.py"

# With token
claude mcp add argocd-mcp -e ARGOCD_TOKEN=YOUR_ARGOCD_TOKEN -- "uv run $(pwd)/server.py"

# Verify it was added
claude mcp list

# For debugging, you can use MCP Inspector with 'mcp dev' command
```

#### Using Claude Desktop

Create a `claude_desktop_config.json` configuration file:

```json
{
  "mcpServers": {
    "argocd-mcp": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/argocd-mcp",
        "run",
        "server.py"
      ],
      "env": {
        "ARGOCD_TOKEN": "your_argocd_token",
        "ARGOCD_API_URL": "https://your-argocd-server.com/api/v1",
        "ARGOCD_VERIFY_SSL": "true"
      }
    }
  }
}
```

Replace the paths and configuration values with your actual values:
- Use the full path to the uv executable (find it with `which uv` on macOS/Linux or `where uv` on Windows)
- Set the correct directory path to your argocd-mcp installation
- Add your ArgoCD API token
- Configure other environment variables as needed

This configuration tells Claude Desktop how to start the MCP server automatically with your specific environment settings.

## Available Tools

### Session Tools

- `get_user_info`: Get the current user's info via api/v1/session/userinfo

### Settings Tools

- `get_settings`: Get ArgoCD server settings including UI, OIDC, and other configurations
- `get_plugins`: Get information about configured ArgoCD plugins

### Version Tools

- `get_version`: Get version information of the API server

### Application Management Tools

- `list_applications`: Get all applications with filtering options
- `get_application_details`: Get detailed information about a specific application
- `create_application`: Create a new application
- `update_application`: Update an existing application
- `delete_application`: Delete an application
- `sync_application`: Trigger a sync operation on an application

## Example Conversations

### Checking User Information

```
User: What's my user information in ArgoCD?

Claude: Let me retrieve your user information.

⏺ argocd-mcp:get_user_info (MCP)
  ⎿  {"loggedIn": true, "username": "devops-user", "iss": "argocd"}

You are logged in as 'devops-user'.
```

### Getting ArgoCD Version

```
User: What version of ArgoCD is running on the server?

Claude: Let me check the ArgoCD version information.

⏺ argocd-mcp:get_version (MCP)
  ⎿  {
        "Version": "v2.9.3+5eaf684",
        "BuildDate": "2023-09-15T14:25:11Z",
        "GitCommit": "5eaf68452",
        "GitTreeState": "clean",
        "GoVersion": "go1.20.7",
        "Compiler": "gc",
        "Platform": "linux/amd64",
        "KustomizeVersion": "v5.1.1",
        "HelmVersion": "v3.12.3",
        "KubectlVersion": "v1.27.4",
        "JsonnetVersion": "v0.20.0"
      }

You're running ArgoCD v2.9.3, built on September 15, 2023. It's running on Linux (amd64) with Go 1.20.7, and includes Kustomize v5.1.1 and Helm v3.12.3.
```

### Getting ArgoCD Settings

```
User: Show me the ArgoCD server settings

Claude: Let me retrieve the ArgoCD server settings for you.

⏺ argocd-mcp:get_settings (MCP)
  ⎿  {
        "clusterSettings": {
          "appLabelKey": "argocd.argoproj.io/instance",
          "controllerNamespace": "argocd",
          "execEnabled": true,
          "statusBadgeEnabled": true,
          "uiBannerContent": "This is a development instance of ArgoCD",
          "url": "https://argocd.example.com"
        }
      }

Here are the key settings for your ArgoCD server:
- URL: https://argocd.example.com
- Controller namespace: argocd
- Exec enabled: Yes
- Status badge enabled: Yes
- UI Banner: "This is a development instance of ArgoCD"
```

### Managing Applications

```
User: What applications do I have in the "production" project?

Claude: Let me list your applications in the production project.

⏺ argocd-mcp:list_applications (MCP)
  ⎿  {
        "items": [
          {
            "metadata": {
              "name": "frontend-app",
            },
            "status": {
              "sync": {"status": "Synced"},
              "health": {"status": "Healthy"},
            }
          },
          {
            "metadata": {
              "name": "api-service",
            },
            "status": {
              "sync": {"status": "OutOfSync"},
              "health": {"status": "Healthy"},
            }
          },
          {
            "metadata": {
              "name": "database",
            },
            "status": {
              "sync": {"status": "Synced"},
              "health": {"status": "Degraded"},
            }
          }
        ]
      }

You have 3 applications in the production project:
- frontend-app (Synced, Healthy)
- api-service (OutOfSync, Healthy)
- database (Synced, Degraded)
```

```
User: Sync the api-service application

Claude: I'll sync the api-service application for you.

⏺ argocd-mcp:sync_application (MCP)
  ⎿  {
        "resourcesResult": {
          "updated": ["Deployment/api-service"],
          "hooks": []
        },
        "status": "Syncing"
      }

Application sync initiated successfully. The sync operation is now in progress.
```

## Development

### Requirements

- Python 3.12+
- MCP (includes FastMCP and development tools)
- uv package manager (recommended) or pip
- ArgoCD API token

### Type Checking

This project uses mypy for static type checking to enhance code quality and catch type-related bugs early:

```bash
# Install mypy
uv pip install mypy

# Run type checking
uv run -m mypy .
```

Type checking configuration is available in both `pyproject.toml` and `mypy.ini`. The configuration enforces strict typing rules including:

- Disallowing untyped definitions
- Warning on returning Any types
- Checking completeness of function definitions
- Namespace packages support
- Module-specific configurations

### Project Structure

The code is organized into a modular structure:

```
argocd-mcp/
├── api/              # API client and communication
│   ├── __init__.py
│   └── client.py     # HTTP client for ArgoCD API
├── models/           # Data models
│   ├── __init__.py
│   └── applications.py # Application data structures
├── tools/            # MCP tools implementation
│   ├── __init__.py
│   ├── session.py    # Session tools (user info)
│   ├── applications.py # Application management tools
│   ├── settings.py   # Server settings tools
│   └── version.py    # Version information tools
├── utils/            # Utility functions
│   ├── __init__.py
├── server.py         # Main server entry point
├── pyproject.toml    # Project configuration and dependencies
└── mypy.ini          # Mypy type checking configuration
```

### Extending the Server

To add new features:
1. Add new tools to the appropriate module in the `tools` directory
2. Register new tools in `server.py`
3. Follow the existing patterns for parameter validation and error handling
4. Update documentation in README.md
5. Add tests for new functionality

## Troubleshooting

If you encounter issues:

1. Check server logs (info logging is enabled by default)
2. Note that `Processing request of type CallToolRequest` is informational, not an error
3. If using `mcp dev server.py`, the MCP Inspector will automatically open at http://localhost:5173 for debugging
4. Use the server logs to debug API calls and responses
5. For SSL certificate issues with self-signed certificates:

```bash
# Disable SSL verification
export ARGOCD_VERIFY_SSL=false
uv run server.py
```

6. Check if all required environment variables are properly set:

```bash
# Show all current ArgoCD environment variables
env | grep ARGOCD
```

## Contributing

Contributions are welcome! Please open an issue or pull request if you'd like to contribute to this project.

When contributing, please follow these guidelines:
- Ensure all code includes proper type hints
- Run mypy type checking before submitting PRs
- Add tests for new functionality
- Update documentation for any new features or changes