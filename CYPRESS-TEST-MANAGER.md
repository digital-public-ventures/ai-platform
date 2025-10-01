# Cypress Test Manager

A comprehensive script for managing Cypress test infrastructure with flexible Ollama configurations.

## Features

- **Dual Ollama Modes**: Choose between local Ollama (fast) or Docker Ollama (isolated)
- **Clean Database**: Fresh database on each restart for consistent testing
- **Health Checks**: Automatic service health verification
- **Color Output**: Clear, colorful status messages
- **Convenience Commands**: Simple shortcuts for common operations

## Quick Start

```bash
# Make executable (first time only)
chmod +x cypress-test-manager.sh

# Start with local Ollama (fastest)
./cypress-test-manager.sh local

# Run tests
./cypress-test-manager.sh test local

# Stop services
./cypress-test-manager.sh down
```

## Commands

| Command          | Description                         |
| ---------------- | ----------------------------------- |
| `up [mode]`      | Start the test environment          |
| `down`           | Stop the test environment           |
| `restart [mode]` | Restart the test environment        |
| `status`         | Show status of services             |
| `logs [service]` | Show logs from services             |
| `test [mode]`    | Run Cypress tests headlessly        |
| `open [mode]`    | Open Cypress GUI                    |
| `clean`          | Clean up all containers and volumes |

## Ollama Modes

### Local Mode (Recommended)

- **Faster startup** - No Docker Ollama needed
- **Uses your local Ollama** instance on port 11434
- **Clean database** on each restart
- **Requires**: Local Ollama running (`ollama serve`)

```bash
./cypress-test-manager.sh up local
./cypress-test-manager.sh test local
```

### Docker Mode

- **Fully isolated** - Everything runs in Docker
- **Slower startup** - Downloads and starts Ollama model
- **Consistent environment** - Same across all machines

```bash
./cypress-test-manager.sh up docker
./cypress-test-manager.sh test docker
```

## Examples

```bash
# Quick shortcuts
./cypress-test-manager.sh local              # Start with local Ollama
./cypress-test-manager.sh docker             # Start with Docker Ollama

# Full commands
./cypress-test-manager.sh up local           # Start services with local Ollama
./cypress-test-manager.sh test local         # Run tests with local Ollama
./cypress-test-manager.sh restart docker     # Restart with Docker Ollama
./cypress-test-manager.sh open local         # Open Cypress GUI
./cypress-test-manager.sh status             # Check service status
./cypress-test-manager.sh logs               # View all service logs
./cypress-test-manager.sh clean              # Clean everything
```

## Prerequisites

### For Local Mode

```bash
# Install and start Ollama locally
brew install ollama
ollama serve

# Pull required model
ollama pull qwen:0.5b-chat-v1.5-q2_K
```

### For Docker Mode

- Docker and Docker Compose installed
- No local Ollama needed

## Debugging

The script follows file-based debugging practices:

- **Screenshots**: Saved to `cypress/screenshots/`
- **Videos**: Saved to `cypress/videos/`
- **Logs**: Available via `./cypress-test-manager.sh logs`

## Service URLs

- **Open WebUI**: http://localhost:8000
- **Local Ollama**: http://localhost:11434 (local mode only)
- **Docker Ollama**: Internal network (docker mode only)

## Troubleshooting

### Local Ollama Not Running

```
❌ Local Ollama is not running on port 11434!
   Please start Ollama locally first:
   - Run: ollama serve
   - Or: brew services start ollama
```

### Service Health Checks

```bash
./cypress-test-manager.sh status
```

### View Logs

```bash
./cypress-test-manager.sh logs              # All services
./cypress-test-manager.sh logs open-webui   # Specific service
```

### Clean Reset

```bash
./cypress-test-manager.sh clean    # Remove everything
./cypress-test-manager.sh up local # Fresh start
```
