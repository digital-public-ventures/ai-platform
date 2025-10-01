#!/bin/bash

# Cypress Integration Test Runner
# Replicates the GitHub workflow cypress-run job locally

set -e

echo "🧪 Starting Cypress Integration Tests..."
echo "This replicates the GitHub workflow cypress-run job"
echo

# Create logs directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo
    echo "🧹 Cleaning up..."
    docker compose -f docker-compose.cypress.yaml down --remove-orphans
    # Optional: clean up Docker build cache (like in the workflow)
    # docker builder prune --all --force
}

# Set trap for cleanup
trap cleanup EXIT

# Build and start services
echo "🏗️  Starting services..."
docker compose -f docker-compose.cypress.yaml up --detach ollama open-webui stable-diffusion-webui model-preloader

echo
echo "⏳ Waiting for services to be ready..."
echo "   - Ollama API"
echo "   - Open WebUI"
echo "   - Stable Diffusion WebUI"

# Wait for services (the compose file handles this with healthchecks)
echo "✅ Services are starting up with health checks..."

# Run the tests
echo
echo "🎯 Running Cypress tests..."
docker compose -f docker-compose.cypress.yaml up cypress

# Collect logs
echo
echo "📋 Collecting logs..."
docker compose -f docker-compose.cypress.yaml up log-collector

# Show results
echo
echo "🎉 Cypress Integration Tests Complete!"
echo
echo "📁 Results Location:"
echo "   Videos: cypress/videos/"
echo "   Screenshots: cypress/screenshots/"
echo "   Logs: logs/compose-logs.txt"
echo
echo "🔍 To view test results:"
echo "   - Check cypress/videos/ for test recordings"
echo "   - Check cypress/screenshots/ for failure screenshots"
echo "   - Check logs/compose-logs.txt for service logs"
echo
echo "🐳 To view service logs in real-time:"
echo "   docker compose -f docker-compose.cypress.yaml logs -f"
echo
echo "🧹 Services will be cleaned up automatically"
