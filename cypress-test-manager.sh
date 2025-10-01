#!/bin/bash

# Cypress Test Manager
# Comprehensive script for managing Cypress test infrastructure
# Usage: ./cypress-test-manager.sh [COMMAND] [OLLAMA_MODE]

set -e

SCRIPT_NAME="$(basename "$0")"
COMPOSE_FILE="docker-compose.cypress.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print usage information
usage() {
    cat << EOF
${CYAN}🧪 Cypress Test Manager${NC}

${YELLOW}USAGE:${NC}
    ${SCRIPT_NAME} [COMMAND] [OLLAMA_MODE]

${YELLOW}COMMANDS:${NC}
    ${GREEN}up${NC}       Start the test environment
    ${GREEN}down${NC}     Stop the test environment  
    ${GREEN}restart${NC}  Restart the test environment
    ${GREEN}build${NC}    Build Open WebUI from local source
    ${GREEN}status${NC}   Show status of services
    ${GREEN}logs${NC}     Show logs from services
    ${GREEN}test${NC}     Run Cypress tests
    ${GREEN}open${NC}     Open Cypress GUI
    ${GREEN}clean${NC}    Clean up all containers and volumes

${YELLOW}OLLAMA_MODE:${NC}
    ${BLUE}local${NC}    Use local Ollama instance (faster startup)
    ${BLUE}docker${NC}   Use Docker Ollama service (fully isolated)

${YELLOW}EXAMPLES:${NC}
    ${SCRIPT_NAME} up local           # Start with local Ollama
    ${SCRIPT_NAME} up docker          # Start with Docker Ollama  
    ${SCRIPT_NAME} test local         # Run tests with local Ollama
    ${SCRIPT_NAME} restart docker     # Restart with Docker Ollama
    ${SCRIPT_NAME} down               # Stop all services
    ${SCRIPT_NAME} status             # Check service status
    ${SCRIPT_NAME} logs               # View service logs
    ${SCRIPT_NAME} clean              # Clean everything

${YELLOW}SHORTCUTS:${NC}
    ${SCRIPT_NAME} local              # Equivalent to: up local
    ${SCRIPT_NAME} docker             # Equivalent to: up docker

EOF
}

# Check if local Ollama is running
check_local_ollama() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check and stop running services with feedback
check_and_stop_services() {
    local command_name=$1
    
    # Check if any services are running
    local running_services
    running_services=$(docker compose -f "$COMPOSE_FILE" ps --services --filter "status=running" 2>/dev/null || true)
    
    if [[ -n "$running_services" ]]; then
        print_color $YELLOW "⚠️  Found running services for $command_name:"
        docker compose -f "$COMPOSE_FILE" ps
        print_color $CYAN "🛑 Stopping existing services..."
        stop_services
        
        # Wait for services to be fully stopped
        print_color $YELLOW "⏳ Waiting for services to stop completely..."
        local timeout=30
        local count=0
        local still_running
        
        while true; do
            still_running=$(docker compose -f "$COMPOSE_FILE" ps --services --filter "status=running" 2>/dev/null || true)
            if [[ -z "$still_running" ]]; then
                break
            fi
            
            sleep 1
            count=$((count + 1))
            if [ $count -ge $timeout ]; then
                print_color $RED "❌ Timeout waiting for services to stop"
                print_color $YELLOW "   Forcing cleanup..."
                docker compose -f "$COMPOSE_FILE" down --remove-orphans
                break
            fi
        done
        
        print_color $GREEN "✅ All services stopped successfully"
    fi
}

# Start services
start_services() {
    local mode=$1
    
    print_color $CYAN "🚀 Starting Cypress test environment..."
    
    if [[ "$mode" == "local" ]]; then
        print_color $BLUE "📋 Mode: Local Ollama"
        
        # Check if local Ollama is running
        print_color $YELLOW "🔍 Checking local Ollama..."
        if ! check_local_ollama; then
            print_color $RED "❌ Local Ollama is not running on port 11434!"
            print_color $YELLOW "   Please start Ollama locally first:"
            print_color $YELLOW "   - Run: ollama serve"
            print_color $YELLOW "   - Or: brew services start ollama"
            exit 1
        fi
        print_color $GREEN "✅ Local Ollama is running!"
        
        # Start services with local-ollama profile
        print_color $YELLOW "🐳 Starting Docker services (Open WebUI with local Ollama)..."
        docker compose -f "$COMPOSE_FILE" --profile local-ollama up -d
        
    elif [[ "$mode" == "docker" ]]; then
        print_color $BLUE "📋 Mode: Docker Ollama"
        print_color $YELLOW "🐳 Starting Docker services (with Docker Ollama)..."
        docker compose -f "$COMPOSE_FILE" --profile docker-ollama up -d
        
    else
        print_color $RED "❌ Invalid Ollama mode: $mode"
        print_color $YELLOW "   Valid options: local, docker"
        exit 1
    fi
    
    # Wait for services to be healthy
    print_color $YELLOW "⏳ Waiting for services to be ready..."
    
    local timeout=120
    local count=0
    
    if [[ "$mode" == "docker" ]]; then
        print_color $YELLOW "   - Waiting for Docker Ollama..."
        while ! docker exec ollama ollama list > /dev/null 2>&1; do
            sleep 2
            count=$((count + 2))
            if [ $count -ge $timeout ]; then
                print_color $RED "❌ Timeout waiting for Docker Ollama"
                docker compose -f "$COMPOSE_FILE" logs ollama
                exit 1
            fi
        done
    fi
    
    print_color $YELLOW "   - Waiting for Open WebUI..."
    while ! curl -s http://localhost:8000/health > /dev/null 2>&1; do
        sleep 2
        count=$((count + 2))
        if [ $count -ge $timeout ]; then
            print_color $RED "❌ Timeout waiting for Open WebUI"
            if [[ "$mode" == "local" ]]; then
                docker compose -f "$COMPOSE_FILE" logs open-webui-local
            else
                docker compose -f "$COMPOSE_FILE" logs open-webui
            fi
            exit 1
        fi
    done
    
    print_color $GREEN "✅ Services are ready!"
    print_color $PURPLE "📱 Open WebUI is available at: http://localhost:8000"
    
    if [[ "$mode" == "local" ]]; then
        print_color $PURPLE "🤖 Using local Ollama at: http://localhost:11434"
    else
        print_color $PURPLE "🤖 Using Docker Ollama (internal)"
    fi
    
    print_color $CYAN ""
    print_color $CYAN "🧪 Ready for testing! You can now:"
    print_color $CYAN "   ${SCRIPT_NAME} test ${mode}     # Run Cypress tests"
    print_color $CYAN "   ${SCRIPT_NAME} open ${mode}     # Open Cypress GUI"
    print_color $CYAN "   ${SCRIPT_NAME} logs             # View service logs"
}

# Build services from local source
build_services() {
    local mode=${1:-"local"}
    
    print_color $CYAN "🔨 Building Open WebUI from local source..."
    print_color $BLUE "📋 Mode: $(echo "$mode" | tr '[:lower:]' '[:upper:]') Ollama"
    
    local profile_arg=""
    if [[ "$mode" == "local" ]]; then
        profile_arg="--profile local-ollama"
    else
        profile_arg="--profile docker-ollama"
    fi
    
    print_color $YELLOW "🔧 Building Docker images..."
    if docker compose -f "$COMPOSE_FILE" $profile_arg build --no-cache; then
        print_color $GREEN "✅ Build completed successfully!"
        print_color $CYAN ""
        print_color $CYAN "🚀 You can now start the services:"
        print_color $CYAN "   ${SCRIPT_NAME} up ${mode}      # Start services"
        print_color $CYAN "   ${SCRIPT_NAME} restart ${mode} # Restart services"
    else
        print_color $RED "❌ Build failed!"
        exit 1
    fi
}

# Stop services
stop_services() {
    print_color $CYAN "🛑 Stopping Cypress test environment..."
    
    # Clean up SQLite database before stopping services
    print_color $YELLOW "🗑️  Cleaning up persistent database..."
    if docker exec open-webui-local test -f /app/backend/data/webui.db 2>/dev/null; then
        docker exec open-webui-local rm -f /app/backend/data/webui.db
        print_color $GREEN "✅ Database file removed"
    elif docker exec open-webui test -f /app/backend/data/webui.db 2>/dev/null; then
        docker exec open-webui rm -f /app/backend/data/webui.db
        print_color $GREEN "✅ Database file removed"
    else
        print_color $YELLOW "ℹ️  No database file found to clean up"
    fi
    
    # Stop and remove all containers with volumes
    print_color $YELLOW "🛑 Stopping containers and removing volumes..."
    docker compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    
    # Stop any remaining Cypress containers that might be running
    print_color $YELLOW "🧹 Cleaning up stray containers..."
    local stray_containers=$(docker ps -a --filter "name=cypress" --filter "name=postgres-cypress" --filter "name=open-webui-local" --format "{{.Names}}" 2>/dev/null || true)
    if [[ -n "$stray_containers" ]]; then
        echo "$stray_containers" | xargs -r docker stop 2>/dev/null || true
        echo "$stray_containers" | xargs -r docker rm 2>/dev/null || true
        print_color $GREEN "✅ Stray containers cleaned up"
    fi
    
    # Clean up any remaining Cypress volumes
    print_color $YELLOW "🗂️  Cleaning up remaining volumes..."
    local cypress_volumes=$(docker volume ls --filter "name=cypress" --format "{{.Name}}" 2>/dev/null || true)
    if [[ -n "$cypress_volumes" ]]; then
        echo "$cypress_volumes" | xargs -r docker volume rm 2>/dev/null || true
        print_color $GREEN "✅ Cypress volumes cleaned up"
    fi
    
    # Clean up unused networks
    print_color $YELLOW "🌐 Cleaning up unused networks..."
    docker network prune -f > /dev/null 2>&1 || true
    sleep 2  # Give Docker time to clean up
    print_color $GREEN "✅ Test environment fully cleaned up"
}

# Show status
show_status() {
    print_color $CYAN "📊 Service Status:"
    docker compose -f "$COMPOSE_FILE" ps
    
    print_color $CYAN "🔍 Health Checks:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_color $GREEN "✅ Open WebUI: Healthy (http://localhost:8000)"
    else
        print_color $RED "❌ Open WebUI: Not responding"
    fi
    
    if check_local_ollama; then
        print_color $GREEN "✅ Local Ollama: Running (http://localhost:11434)"
    else
        print_color $YELLOW "⚠️  Local Ollama: Not running"
    fi
}

# Show logs
show_logs() {
    local service=$1
    
    if [[ -n "$service" ]]; then
        print_color $CYAN "📋 Logs for service: $service"
        docker compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        print_color $CYAN "📋 All service logs:"
        docker compose -f "$COMPOSE_FILE" logs -f
    fi
}

# Run Cypress tests
run_tests() {
    local mode=$1
    
    print_color $CYAN "🧪 Running Cypress tests..."
    print_color $BLUE "📋 Mode: $(echo "$mode" | tr '[:lower:]' '[:upper:]') Ollama"
    
    # Ensure services are running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_color $YELLOW "⚠️  Services not running, starting them first..."
        start_services "$mode"
    fi
    
    print_color $YELLOW "🏃 Running tests headlessly..."
    npm run cy:run:local
    
    print_color $CYAN "📸 Test artifacts saved to:"
    print_color $CYAN "   cypress/screenshots/"
    print_color $CYAN "   cypress/videos/"
}

# Open Cypress GUI
open_cypress() {
    local mode=$1
    
    print_color $CYAN "🖥️  Opening Cypress GUI..."
    print_color $BLUE "📋 Mode: $(echo "$mode" | tr '[:lower:]' '[:upper:]') Ollama"
    
    # Ensure services are running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_color $YELLOW "⚠️  Services not running, starting them first..."
        start_services "$mode"
    fi
    
    print_color $YELLOW "🖱️  Opening Cypress Test Runner..."
    npm run cy:open:local
}

# Clean up everything
clean_all() {
    print_color $CYAN "🧹 Cleaning up test environment..."
    
    print_color $YELLOW "🛑 Stopping all services..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans
    
    print_color $YELLOW "🗑️  Removing volumes..."
    docker volume rm open-webui_ollama_data open-webui_open_webui_data open-webui_cypress_videos open-webui_cypress_screenshots 2>/dev/null || true
    
    print_color $YELLOW "🐳 Removing test images..."
    docker image rm open-webui-cypress-test-docker open-webui-cypress-test-local 2>/dev/null || true
    sleep 2  # Give Docker time to clean up
    print_color $GREEN "✅ Cleanup complete"
}

# Parse arguments
COMMAND=${1:-"help"}
OLLAMA_MODE=${2:-"local"}

# Handle shortcuts
case "$COMMAND" in
    "local")
        COMMAND="up"
        OLLAMA_MODE="local"
        ;;
    "docker")
        COMMAND="up"
        OLLAMA_MODE="docker"
        ;;
esac

# Execute command
case "$COMMAND" in
    "up")
        check_and_stop_services "startup"
        start_services "$OLLAMA_MODE"
        ;;
    "down")
        stop_services
        ;;
    "restart")
        check_and_stop_services "restart"
        start_services "$OLLAMA_MODE"
        ;;
    "build")
        build_services "$OLLAMA_MODE"
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$OLLAMA_MODE"
        ;;
    "test")
        run_tests "$OLLAMA_MODE"
        ;;
    "open")
        open_cypress "$OLLAMA_MODE"
        ;;
    "clean")
        clean_all
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        print_color $RED "❌ Unknown command: $COMMAND"
        echo ""
        usage
        exit 1
        ;;
esac
