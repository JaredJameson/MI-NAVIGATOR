#!/bin/bash

# MI-Navigator Development Environment Setup Script
# This script initializes the development environment for the Market Intelligence Navigator

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   MI-Navigator Development Setup          ${NC}"
echo -e "${BLUE}   Market Intelligence Platform            ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for required tools
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed. Please install Node.js 18+ first.${NC}"
        exit 1
    fi
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo -e "${RED}Node.js 18+ required. Current version: $(node -v)${NC}"
        exit 1
    fi
    echo -e "${GREEN}  Node.js: $(node -v)${NC}"

    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}npm is not installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}  npm: $(npm -v)${NC}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.11+ first.${NC}"
        exit 1
    fi
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}  Python: $PYTHON_VERSION${NC}"

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 is not installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}  pip3: $(pip3 --version | cut -d' ' -f2)${NC}"

    # Check Docker (optional but recommended)
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}  Docker: $(docker --version | cut -d' ' -f3 | tr -d ',')${NC}"
        DOCKER_AVAILABLE=true
    else
        echo -e "${YELLOW}  Docker: Not installed (optional - will use local services)${NC}"
        DOCKER_AVAILABLE=false
    fi

    echo -e "${GREEN}All required tools are available.${NC}"
    echo ""
}

# Create project directory structure
create_directory_structure() {
    echo -e "${YELLOW}Creating project directory structure...${NC}"

    # Backend directories
    mkdir -p backend/app/{api,core,db,models,schemas,services,agents,prompts,utils}
    mkdir -p backend/app/api/v1/endpoints
    mkdir -p backend/tests/{unit,integration}
    mkdir -p backend/alembic/versions

    # Frontend directories
    mkdir -p frontend/src/{app,components,hooks,lib,services,stores,types,utils}
    mkdir -p frontend/src/app/{auth,dashboard,reports,projects,chat,settings}
    mkdir -p frontend/src/components/{ui,layout,charts,forms,chat,reports,dashboard}
    mkdir -p frontend/public/images

    # Shared directories
    mkdir -p docker
    mkdir -p scripts
    mkdir -p docs

    echo -e "${GREEN}Directory structure created.${NC}"
    echo ""
}

# Setup backend (FastAPI)
setup_backend() {
    echo -e "${YELLOW}Setting up Backend (FastAPI)...${NC}"

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "Installing backend dependencies..."
        pip install -r requirements.txt
    else
        echo "Creating requirements.txt..."
        cat > requirements.txt << 'EOF'
# FastAPI and ASGI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
websockets==12.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
asyncpg==0.29.0

# Cache
redis==5.0.1
aioredis==2.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# AI / LLM
anthropic==0.18.1
openai==1.12.0

# HTTP Client
httpx==0.26.0
aiohttp==3.9.3

# Web Scraping
beautifulsoup4==4.12.3
playwright==1.41.2
lxml==5.1.0

# PDF Processing
pypdf==4.0.1
pdfplumber==0.10.4

# Document Generation
python-docx==1.1.0
reportlab==4.0.9
openpyxl==3.1.2
python-pptx==0.6.23

# Utilities
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
tenacity==8.2.3
structlog==24.1.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
pytest-cov==4.1.0
httpx==0.26.0

# Development
black==24.1.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
EOF
        pip install -r requirements.txt
    fi

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << 'EOF'
# MI-Navigator Backend Environment Variables

# Application
APP_NAME="MI-Navigator"
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://minavigator:minavigator@localhost:5432/minavigator
ASYNC_DATABASE_URL=postgresql+asyncpg://minavigator:minavigator@localhost:5432/minavigator

# Redis
REDIS_URL=redis://localhost:6379/0

# Claude AI
ANTHROPIC_API_KEY=your-anthropic-api-key

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# External APIs (optional)
SIMILARWEB_API_KEY=
SERPAPI_KEY=
PROXYCURL_API_KEY=
EOF
    fi

    deactivate
    cd ..

    echo -e "${GREEN}Backend setup complete.${NC}"
    echo ""
}

# Setup frontend (Next.js 14)
setup_frontend() {
    echo -e "${YELLOW}Setting up Frontend (Next.js 14)...${NC}"

    cd frontend

    # Initialize package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        echo "Creating package.json..."
        cat > package.json << 'EOF'
{
  "name": "mi-navigator-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@tanstack/react-query": "5.18.0",
    "zustand": "4.5.0",
    "axios": "1.6.7",
    "date-fns": "3.3.1",
    "clsx": "2.1.0",
    "tailwind-merge": "2.2.1",
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-dropdown-menu": "2.0.6",
    "@radix-ui/react-select": "2.0.0",
    "@radix-ui/react-tabs": "1.0.4",
    "@radix-ui/react-toast": "1.1.5",
    "@radix-ui/react-tooltip": "1.0.7",
    "@radix-ui/react-checkbox": "1.0.4",
    "@radix-ui/react-label": "2.0.2",
    "@radix-ui/react-slot": "1.0.2",
    "lucide-react": "0.323.0",
    "framer-motion": "11.0.5",
    "recharts": "2.12.0",
    "react-markdown": "9.0.1",
    "socket.io-client": "4.7.4",
    "class-variance-authority": "0.7.0"
  },
  "devDependencies": {
    "@types/node": "20.11.16",
    "@types/react": "18.2.55",
    "@types/react-dom": "18.2.19",
    "autoprefixer": "10.4.17",
    "eslint": "8.56.0",
    "eslint-config-next": "14.1.0",
    "postcss": "8.4.35",
    "tailwindcss": "3.4.1",
    "typescript": "5.3.3",
    "jest": "29.7.0",
    "@testing-library/react": "14.2.1",
    "@testing-library/jest-dom": "6.4.2"
  }
}
EOF
    fi

    # Install dependencies
    echo "Installing frontend dependencies..."
    npm install

    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        echo "Creating .env.local..."
        cat > .env.local << 'EOF'
# MI-Navigator Frontend Environment Variables

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=MI-Navigator
EOF
    fi

    # Create tailwind.config.js if it doesn't exist
    if [ ! -f "tailwind.config.js" ]; then
        echo "Creating tailwind.config.js..."
        cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}
EOF
    fi

    # Create next.config.js if it doesn't exist
    if [ ! -f "next.config.js" ]; then
        echo "Creating next.config.js..."
        cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
EOF
    fi

    cd ..

    echo -e "${GREEN}Frontend setup complete.${NC}"
    echo ""
}

# Setup Docker services
setup_docker_services() {
    echo -e "${YELLOW}Setting up Docker services...${NC}"

    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: mi-navigator-postgres
    environment:
      POSTGRES_USER: minavigator
      POSTGRES_PASSWORD: minavigator
      POSTGRES_DB: minavigator
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U minavigator"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: mi-navigator-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Qdrant for vector search (future use)
  qdrant:
    image: qdrant/qdrant:latest
    container_name: mi-navigator-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

networks:
  default:
    name: mi-navigator-network
EOF

    echo -e "${GREEN}Docker compose file created.${NC}"
    echo ""
}

# Start development services
start_services() {
    echo -e "${YELLOW}Starting development services...${NC}"

    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo "Starting Docker services (PostgreSQL, Redis)..."
        docker-compose up -d postgres redis

        # Wait for services to be healthy
        echo "Waiting for services to be ready..."
        sleep 5

        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo -e "${GREEN}Docker services are running.${NC}"
        else
            echo -e "${RED}Failed to start Docker services.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Docker not available. Please ensure PostgreSQL and Redis are running locally.${NC}"
        echo "PostgreSQL should be accessible at: localhost:5432"
        echo "Redis should be accessible at: localhost:6379"
    fi

    echo ""
}

# Print startup instructions
print_instructions() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Setup Complete!                         ${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "${GREEN}To start the development servers:${NC}"
    echo ""
    echo -e "  ${YELLOW}Backend (Terminal 1):${NC}"
    echo "    cd backend"
    echo "    source venv/bin/activate"
    echo "    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo -e "  ${YELLOW}Frontend (Terminal 2):${NC}"
    echo "    cd frontend"
    echo "    npm run dev"
    echo ""
    echo -e "${GREEN}Access the application:${NC}"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo -e "${GREEN}Database services:${NC}"
    echo "  PostgreSQL: localhost:5432 (user: minavigator, pass: minavigator)"
    echo "  Redis: localhost:6379"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo "  1. Update backend/.env with your ANTHROPIC_API_KEY"
    echo "  2. Run database migrations before first use"
    echo "  3. Check docs/ for detailed documentation"
    echo ""
    echo -e "${BLUE}Happy coding!${NC}"
}

# Main execution
main() {
    echo ""

    # Change to project directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    check_requirements
    create_directory_structure
    setup_backend
    setup_frontend
    setup_docker_services
    start_services
    print_instructions
}

# Run main function
main
