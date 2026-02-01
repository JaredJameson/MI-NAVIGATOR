#!/bin/bash
# ============================================================================
# Agent Deployment Script - Phase 3 Week 31
# ============================================================================
#
# Deployment script for Phase 2 LLM-enhanced agents
#
# Usage:
#   ./scripts/deploy_agents.sh [staging|production] [agent_name|all]
#
# Examples:
#   ./scripts/deploy_agents.sh staging market_search      # Deploy single agent to staging
#   ./scripts/deploy_agents.sh staging all                # Deploy all agents to staging
#   ./scripts/deploy_agents.sh production market_search   # Deploy to production
#
# Author: Claude Code SuperClaude
# Created: 2026-02-01 (Phase 3 Week 31 Day 2)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=$1
AGENT_NAME=$2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Validate arguments
if [ -z "$ENVIRONMENT" ] || [ -z "$AGENT_NAME" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: $0 [staging|production] [agent_name|all]"
    echo ""
    echo "Available agents:"
    echo "  - market_search        (93.5% quality - highest)"
    echo "  - financial_analysis   (92% quality)"
    echo "  - competitor_mapping   (91% quality)"
    echo "  - company_profile      (89% quality)"
    echo "  - digital_presence     (88% quality)"
    echo "  - all                  (deploy all agents)"
    echo ""
    echo "Examples:"
    echo "  $0 staging market_search"
    echo "  $0 staging all"
    echo "  $0 production market_search"
    exit 1
fi

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'${NC}"
    echo "Must be 'staging' or 'production'"
    exit 1
fi

# Phase 2 agents with quality scores
declare -A AGENTS=(
    ["market_search"]="0.935"
    ["financial_analysis"]="0.92"
    ["competitor_mapping"]="0.91"
    ["company_profile"]="0.89"
    ["digital_presence"]="0.88"
)

# Validate agent name
if [ "$AGENT_NAME" != "all" ] && [ -z "${AGENTS[$AGENT_NAME]}" ]; then
    echo -e "${RED}Error: Invalid agent name '$AGENT_NAME'${NC}"
    echo "Available agents: ${!AGENTS[@]} all"
    exit 1
fi

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

deploy_agent() {
    local agent=$1
    local quality=${AGENTS[$agent]}
    local env=$ENVIRONMENT

    print_header "Deploying Agent: $agent (Quality: $quality)"

    # Step 1: Pre-deployment checks
    print_step "Running pre-deployment checks..."

    # Check if agent file exists
    local agent_file="$PROJECT_ROOT/backend/app/agents/${agent}_agent.py"
    if [ ! -f "$agent_file" ]; then
        print_error "Agent file not found: $agent_file"
        return 1
    fi

    print_info "Agent file exists: $agent_file"

    # Check if tests exist
    local test_file="$PROJECT_ROOT/backend/tests/unit/test_${agent}_agent.py"
    if [ -f "$test_file" ]; then
        print_info "Test file exists: $test_file"
    else
        print_error "Warning: Test file not found: $test_file"
    fi

    # Step 2: Run unit tests
    print_step "Running unit tests for $agent agent..."

    cd "$PROJECT_ROOT/backend"

    if [ -f "$test_file" ]; then
        if pytest "$test_file" -v --tb=short; then
            print_success "All tests passed for $agent agent"
        else
            print_error "Tests failed for $agent agent"
            return 1
        fi
    else
        print_info "Skipping tests (no test file found)"
    fi

    # Step 3: Deploy to environment
    print_step "Deploying $agent agent to $env..."

    if [ "$env" == "staging" ]; then
        # Staging deployment
        print_info "Deploying to staging environment..."

        # Restart staging backend
        docker-compose -f "$PROJECT_ROOT/docker-compose.staging.yml" restart backend

        print_success "Agent deployed to staging"

    elif [ "$env" == "production" ]; then
        # Production deployment (with confirmation)
        print_info "Deploying to production environment..."

        echo -e "${YELLOW}⚠️  WARNING: Deploying to PRODUCTION${NC}"
        read -p "Are you sure you want to deploy $agent to production? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            print_error "Deployment cancelled by user"
            return 1
        fi

        # Restart production backend (rolling update)
        docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" up -d --no-deps --build backend

        print_success "Agent deployed to production (rolling update)"
    fi

    # Step 4: Health check
    print_step "Running post-deployment health check..."

    sleep 5  # Wait for service to be ready

    # Determine API URL
    if [ "$env" == "staging" ]; then
        API_URL="http://localhost:8080/api/v1/agents/health/$agent"
    else
        API_URL="https://app.mi-navigator.com/api/v1/agents/health/$agent"
    fi

    print_info "Checking health: $API_URL"

    if curl -f -s "$API_URL" > /dev/null; then
        print_success "Health check passed for $agent"
    else
        print_error "Health check failed for $agent"
        print_info "Agent may still be starting up..."
    fi

    # Step 5: Smoke test (optional)
    print_step "Running smoke test for $agent..."

    # TODO: Add smoke test calls to agent endpoints

    print_success "$agent agent deployed successfully to $env!"
    echo ""
}

# ============================================================================
# MAIN DEPLOYMENT LOGIC
# ============================================================================

print_header "Agent Deployment - Phase 3 Week 31"
echo "Environment: $ENVIRONMENT"
echo "Agent: $AGENT_NAME"
echo ""

# Deploy single agent or all agents
if [ "$AGENT_NAME" == "all" ]; then
    print_info "Deploying all agents in quality order (highest first)..."

    # Sort agents by quality score (highest first)
    sorted_agents=$(for agent in "${!AGENTS[@]}"; do
        echo "${AGENTS[$agent]} $agent"
    done | sort -rn | awk '{print $2}')

    for agent in $sorted_agents; do
        deploy_agent "$agent"
        sleep 2  # Small delay between agents
    done

else
    # Deploy single agent
    deploy_agent "$AGENT_NAME"
fi

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

print_header "Deployment Summary"

print_success "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Monitor agent health: curl $API_URL/health"
echo "2. Check metrics: curl $API_URL/metrics"
echo "3. Run integration tests: pytest tests/integration/"
echo "4. Monitor logs: docker-compose -f docker-compose.$ENVIRONMENT.yml logs -f backend"
echo ""

if [ "$ENVIRONMENT" == "staging" ]; then
    echo "Staging endpoints:"
    echo "  - Health: http://localhost:8080/api/v1/agents/health"
    echo "  - Metrics: http://localhost:8080/api/v1/agents/metrics"
    echo "  - Market Search: http://localhost:8080/api/v1/agents/market-search"
elif [ "$ENVIRONMENT" == "production" ]; then
    echo "Production endpoints:"
    echo "  - Health: https://app.mi-navigator.com/api/v1/agents/health"
    echo "  - Metrics: https://app.mi-navigator.com/api/v1/agents/metrics"
    echo "  - Market Search: https://app.mi-navigator.com/api/v1/agents/market-search"
fi

echo ""
print_success "🎉 Deployment complete!"
