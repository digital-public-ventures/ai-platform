#!/bin/bash

# Local Test Manager - Fast Local Development with PostgreSQL Container
# Uses PostgreSQL Docker container + local backend dev server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Emojis for better visual feedback
SUCCESS="✅"
WARNING="⚠️"
INFO="ℹ️"
STOP="🛑"
CLEANUP="🧹"
START="🚀"
DB="🗃️"

# PID files for tracking processes
BACKEND_PID_FILE="/tmp/open-webui-backend.pid"

# PostgreSQL container name
POSTGRES_CONTAINER="postgres-local-test"

# Function to kill processes on a specific port
kill_port() {
    local port="$1"
    echo -e "${CLEANUP} Cleaning up processes on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
}

# Function to check if a process is running
is_process_running() {
    local pid_file="$1"
    if [[ -f "$pid_file" ]]; then
        local pid
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Process is running
        else
            rm -f "$pid_file"  # Clean up stale PID file
            return 1  # Process not running
        fi
    fi
    return 1  # PID file doesn't exist
}

# Function to kill process by PID file
kill_process() {
    local pid_file="$1"
    local name="$2"
    if [[ -f "$pid_file" ]]; then
        local pid
        pid=$(cat "$pid_file")
        echo -e "${STOP} Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${WARNING} Force killing $name..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$pid_file"
        echo -e "${SUCCESS} $name stopped"
    fi
}

# Function to start PostgreSQL container
start_postgres() {
    echo -e "${DB} Starting PostgreSQL container..."
    
    # Stop and remove existing container if it exists
    docker stop "$POSTGRES_CONTAINER" 2>/dev/null || true
    docker rm "$POSTGRES_CONTAINER" 2>/dev/null || true
    
    # Start fresh PostgreSQL container (no volumes for ephemeral data)
    docker run -d \
        --name "$POSTGRES_CONTAINER" \
        -p 5432:5432 \
        -e POSTGRES_DB=openwebui \
        -e POSTGRES_USER=openwebui \
        -e POSTGRES_PASSWORD=openwebui \
        --tmpfs /var/lib/postgresql/data:rw,noexec,nosuid,size=1g \
        postgres:16-alpine
    
    echo -e "${SUCCESS} PostgreSQL container started"
    
    # Wait for PostgreSQL to be ready
    echo -e "${INFO} Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec "$POSTGRES_CONTAINER" pg_isready -U openwebui -d openwebui > /dev/null 2>&1; then
            echo -e "${SUCCESS} PostgreSQL is ready"
            return 0
        fi
        echo -e "${INFO} Waiting for PostgreSQL... ($i/30)"
        sleep 1
    done
    
    echo -e "${RED} PostgreSQL failed to start within 30 seconds"
    return 1
}

# Function to stop PostgreSQL container
stop_postgres() {
    echo -e "${DB} Stopping PostgreSQL container..."
    docker stop "$POSTGRES_CONTAINER" 2>/dev/null || true
    docker rm "$POSTGRES_CONTAINER" 2>/dev/null || true
    echo -e "${SUCCESS} PostgreSQL container stopped and removed"
}

# Function to start backend
start_backend() {
    echo -e "${START} Starting backend development server..."
    cd backend
    
    # Set environment variables for the backend
    export DATABASE_URL="postgresql://openwebui:openwebui@localhost:5432/openwebui"
    export WEBUI_AUTH=True
    export ENABLE_SIGNUP=True
    export ENABLE_LOGIN_FORM=True
    export ENABLE_PERSISTENT_CONFIG=False
    export OLLAMA_BASE_URL="http://localhost:11434"
    
    # Explicitly override OpenAI variables to ensure Ollama models are prioritized
    # Setting to empty string instead of unsetting to override any .env file values
    export OPENAI_API_KEY=""
    export OPENAI_BASE_URL=""
    export OPENAI_ORGANIZATION=""
    export OPENAI_PROJECT=""
    
    nohup ./dev.sh > /tmp/backend.log 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    cd ..
    echo -e "${SUCCESS} Backend started (PID: $(cat $BACKEND_PID_FILE))"
    echo -e "${INFO} Backend logs: tail -f /tmp/backend.log"
    echo -e "${INFO} Backend URL: http://localhost:8080/"
}

# Function to wait for backend
wait_for_backend() {
    echo -e "${INFO} Waiting for backend to be ready (including migrations)..."
    
    # Give extra time for database migrations
    for i in {1..60}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo -e "${SUCCESS} Backend is ready"
            return 0
        fi
        echo -e "${INFO} Waiting for backend and migrations... ($i/60)"
        sleep 2
    done
    
    echo -e "${RED} Backend failed to start within 2 minutes"
    return 1
}

# Function to check service status
status() {
    echo -e "${INFO} Service Status:"
    
    # Check PostgreSQL container
    if docker ps --filter "name=$POSTGRES_CONTAINER" --format "table {{.Names}}\t{{.Status}}" | grep -q "$POSTGRES_CONTAINER"; then
        echo -e "${SUCCESS} PostgreSQL: Running (container: $POSTGRES_CONTAINER)"
        echo -e "    URL: postgresql://openwebui:openwebui@localhost:5432/openwebui"
    else
        echo -e "${STOP} PostgreSQL: Not running"
    fi
    
    if is_process_running "$BACKEND_PID_FILE"; then
        echo -e "${SUCCESS} Backend: Running (PID: $(cat $BACKEND_PID_FILE))"
        echo -e "    URL: http://localhost:8080/"
    else
        echo -e "${STOP} Backend: Not running"
    fi
    
    # Frontend commented out for now
    # echo -e "${INFO} Frontend: Disabled (using built frontend at backend:8080)"
}

# Function to stop all services
stop_all() {
    echo -e "${STOP} Stopping all local development services..."
    kill_process "$BACKEND_PID_FILE" "Backend"
    
    # Extra cleanup: kill any remaining processes on port 8080
    kill_port 8080
    
    stop_postgres
    echo -e "${CLEANUP} Cleaning up log files..."
    rm -f /tmp/backend.log
    echo -e "${SUCCESS} All services stopped and cleaned up"
}

# Function to start all services
start_all() {
    echo -e "${START} Starting fast local development environment..."
    
    # Check if services are already running
    if is_process_running "$BACKEND_PID_FILE"; then
        echo -e "${WARNING} Backend is already running. Stopping first..."
        stop_all
        sleep 2
    fi
    
    # Check if PostgreSQL is running
    if docker ps --filter "name=$POSTGRES_CONTAINER" --format "{{.Names}}" | grep -q "$POSTGRES_CONTAINER"; then
        echo -e "${WARNING} PostgreSQL container is already running. Stopping first..."
        stop_postgres
        sleep 1
    fi
    
    start_postgres
    start_backend
    
    wait_for_backend
    status
    
    echo -e "${SUCCESS} Fast local development environment is ready!"
    echo -e "${INFO} Backend: http://localhost:8080/"
    echo -e "${INFO} Database: PostgreSQL (ephemeral - no persistence)"
    echo -e "${INFO} Use './local-test-manager.sh status' to check service status"
    echo -e "${INFO} Use './local-test-manager.sh down' to stop all services"
}

# Function to restart services
restart() {
    echo -e "${INFO} Restarting local development environment..."
    stop_all
    sleep 2
    start_all
}

# Function to show logs
logs() {
    local service="$1"
    case "$service" in
        "backend"|"be")
            if [[ -f /tmp/backend.log ]]; then
                tail -f /tmp/backend.log
            else
                echo -e "${WARNING} Backend log not found"
            fi
            ;;
        "postgres"|"db")
            docker logs -f "$POSTGRES_CONTAINER" 2>/dev/null || echo -e "${WARNING} PostgreSQL container not running"
            ;;
        *)
            echo -e "${INFO} Available logs:"
            echo -e "  ./local-test-manager.sh logs backend   # Backend logs"
            echo -e "  ./local-test-manager.sh logs postgres  # PostgreSQL logs"
            ;;
    esac
}

# Main command handling
case "$1" in
    "up"|"start")
        start_all
        ;;
    "down"|"stop")
        stop_all
        ;;
    "restart")
        restart
        ;;
    "status")
        status
        ;;
    "logs")
        logs "$2"
        ;;
    *)
        echo -e "${INFO} Local Test Manager - Fast Local Development with PostgreSQL Container"
        echo ""
        echo "Usage: $0 {up|down|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  up/start    - Start PostgreSQL container and backend development server"
        echo "  down/stop   - Stop all services (backend + PostgreSQL)"
        echo "  restart     - Restart all services"  
        echo "  status      - Show status of all services"
        echo "  logs [be|db] - Show logs (backend or postgres)"
        echo ""
        echo "URLs when running:"
        echo "  Backend:  http://localhost:8080/"
        echo "  Database: postgresql://openwebui:openwebui@localhost:5432/openwebui"
        echo ""
        echo "Features:"
        echo "  - Fast startup (PostgreSQL starts in ~3 seconds)"
        echo "  - Ephemeral database (no persistence between restarts)"
        echo "  - Automatic database migrations on backend startup"
        echo "  - Clean environment for testing"
        echo ""
        exit 1
        ;;
esac
