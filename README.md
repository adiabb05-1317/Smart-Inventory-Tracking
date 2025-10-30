Here's the updated README with Jenkins CI/CD and complete AWS architecture:

---

# 🚀 Smart Inventory Tracking System

A complete full-stack inventory management system with AI-powered insights, automated CI/CD pipeline, and cloud-native architecture on AWS.

## 🏗️ System Architecture

### **Complete Cloud Infrastructure (AWS)**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          AWS Cloud (us-east-1)                            │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    VPC (10.0.0.0/16)                                │ │
│  │                                                                     │ │
│  │  ┌──────────────────────────────────┐  ┌──────────────────────┐  │ │
│  │  │   Public Subnet (10.0.1.0/24)    │  │ Private Subnet       │  │ │
│  │  │                                   │  │ (10.0.2.0/24)        │  │ │
│  │  │  ┌─────────────────────────────┐ │  │                      │  │ │
│  │  │  │ Frontend EC2 (t2.micro)     │ │  │  ┌────────────────┐ │  │ │
│  │  │  │ - Public IP: 3.94.146.75    │ │  │  │ Backend EC2    │ │  │ │
│  │  │  │ - Private IP: 10.0.1.111    │ │  │  │ (t2.small)     │ │  │ │
│  │  │  │ - Docker: Nginx + React     │◄┼──┼─►│ - Private IP:  │ │  │ │
│  │  │  │ - Port 80 (HTTP)            │ │  │  │   10.0.2.214   │ │  │ │
│  │  │  └─────────────────────────────┘ │  │  │ - Docker:      │ │  │ │
│  │  │            ▲                      │  │  │   FastAPI +    │ │  │ │
│  │  │            │                      │  │  │   PostgreSQL   │ │  │ │
│  │  │            │ Internet Gateway     │  │  │ - Port 8000    │ │  │ │
│  │  │            │                      │  │  │ - Port 5432    │ │  │ │
│  │  │  ┌─────────────────────────────┐ │  │  └────────────────┘ │  │ │
│  │  │  │ Jenkins Server (t2.medium)  │ │  │         ▲           │  │ │
│  │  │  │ - Public IP: 54.82.33.47    │ │  │         │           │  │ │
│  │  │  │ - Private IP: 10.0.1.x      │ │  │         │ SSH via   │  │ │
│  │  │  │ - Jenkins: 8080             │ │  │         │ Frontend  │  │ │
│  │  │  │ - Docker + Docker Compose   │◄┼──┼─────────┘           │  │ │
│  │  │  └─────────────────────────────┘ │  │                      │  │ │
│  │  │            ▲                      │  │                      │  │ │
│  │  │            │                      │  │    NAT Gateway       │  │ │
│  │  │            │ Webhook              │  │         ▲            │  │ │
│  │  └────────────┼──────────────────────┘  └─────────┼───────────┘  │ │
│  │               │                                    │              │ │
│  └───────────────┼────────────────────────────────────┼──────────────┘ │
│                  │                                    │                │
│         Internet Gateway                      Outbound Internet        │
└──────────────────┼────────────────────────────────────────────────────┘
                   │
                   │
        ┌──────────▼──────────┐
        │   GitHub Repository  │
        │                     │
        │  Smart-Inventory-   │
        │     Tracking        │
        └─────────────────────┘
                   │
                   │
        ┌──────────▼──────────┐
        │   Docker Hub        │
        │                     │
        │  - inventory-backend│
        │  - inventory-frontend│
        └─────────────────────┘
```

### **Application Stack Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │   PostgreSQL DB │
│   (Vite + TS)   │◄──►│  (Python 3.13)  │◄──►│  (Docker)       │
│                 │    │                 │    │                 │
│ • Zustand Store │    │ • LangChain AI  │    │ • Products      │
│ • Tailwind CSS  │    │ • Cerebras LLM  │    │ • Sales History │
│ • Axios HTTP    │    │ • SQL Executor   │    │ • Analytics     │
│ • Recharts      │    │ • Connection Pool│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Assistant   │
                       │   (LangChain)    │
                       │                 │
                       │ • SQL Executor   │
                       └─────────────────┘
```

***

## 🌐 AWS Infrastructure Details

### **VPC Configuration**
- **CIDR Block:** 10.0.0.0/16
- **Region:** us-east-1 (N. Virginia)
- **Availability Zone:** us-east-1a

### **Subnets**

| Subnet Type | CIDR Block | Purpose | Components |
|-------------|-----------|---------|------------|
| **Public Subnet** | 10.0.1.0/24 | Internet-facing services | Frontend EC2, Jenkins EC2, NAT Gateway |
| **Private Subnet** | 10.0.2.0/24 | Internal services | Backend EC2, PostgreSQL Database |

### **Network Components**

#### **Internet Gateway (IGW)**
- Provides internet access to public subnet
- Attached to VPC
- Enables inbound/outbound internet traffic

#### **NAT Gateway**
- Deployed in public subnet
- Enables outbound internet for private subnet
- Required for backend to pull Docker images

#### **Route Tables**

**Public Route Table:**
```
Destination       Target
10.0.0.0/16      local
0.0.0.0/0        igw-xxxxx (Internet Gateway)
```

**Private Route Table:**
```
Destination       Target
10.0.0.0/16      local
0.0.0.0/0        nat-xxxxx (NAT Gateway)
```

### **Security Groups**

#### **Frontend Security Group** (`inventory-frontend-sg`)

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| HTTP | TCP | 80 | 0.0.0.0/0 | Public web access |
| SSH | TCP | 22 | My IP | Remote management |
| All Traffic | All | All | 0.0.0.0/0 | Outbound |

#### **Backend Security Group** (`inventory-backend-sg`)

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| Custom TCP | TCP | 8000 | 10.0.1.0/24 | API access from frontend |
| Custom TCP | TCP | 5432 | 10.0.2.0/24 | PostgreSQL internal |
| SSH | TCP | 22 | 10.0.1.0/24 | SSH from bastion |
| ICMP | All | All | 10.0.1.0/24 | Network testing |
| All Traffic | All | All | 0.0.0.0/0 | Outbound |

#### **Jenkins Security Group** (`jenkins-sg`)

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| HTTP | TCP | 8080 | 0.0.0.0/0 | Jenkins Web UI |
| SSH | TCP | 22 | My IP | Server management |
| All Traffic | All | All | 0.0.0.0/0 | Outbound |

### **EC2 Instances**

#### **Frontend Server**
- **Type:** t2.micro (1 vCPU, 1GB RAM)
- **AMI:** Ubuntu 22.04 LTS
- **Public IP:** 3.94.146.75
- **Private IP:** 10.0.1.111
- **Docker Containers:**
  - Nginx + React Production Build
  - Port mapping: 80:80

#### **Backend Server**
- **Type:** t2.small (1 vCPU, 2GB RAM)
- **AMI:** Ubuntu 22.04 LTS
- **Public IP:** None (Private subnet)
- **Private IP:** 10.0.2.214
- **Docker Containers:**
  - FastAPI Application (Port 8000)
  - PostgreSQL Database (Port 5432)

#### **Jenkins Server**
- **Type:** t2.medium (2 vCPU, 4GB RAM)
- **AMI:** Ubuntu 22.04 LTS
- **Public IP:** 54.82.33.47
- **Private IP:** 10.0.1.x
- **Services:**
  - Jenkins (Port 8080)
  - Docker Engine
  - Docker Compose

---

## 🔄 CI/CD Pipeline with Jenkins

### **Pipeline Overview**

```
Developer Push to GitHub
        ↓
GitHub Webhook Trigger
        ↓
Jenkins Server (EC2)
        ↓
┌───────────────────────────────────┐
│   Jenkins Pipeline Stages         │
│                                   │
│  1. Checkout Code from GitHub    │
│  2. Build Backend Docker Image   │
│  3. Build Frontend Docker Image  │
│  4. Run Tests                    │
│  5. Push Images to Docker Hub    │
│  6. Deploy Backend to EC2        │
│  7. Deploy Frontend to EC2       │
│  8. Health Check                 │
└───────────────────────────────────┘
        ↓
Application Updated Automatically! ✅
```

### **Jenkins Configuration**

**Installation:** Direct installation on Ubuntu EC2
**Access:** http://54.82.33.47:8080
**Pipeline Type:** Declarative Pipeline (Jenkinsfile)

### **Pipeline Stages**

#### **Stage 1: Checkout**
```groovy
- Clone repository from GitHub
- Branch: main
- Commit SHA tracked
```

#### **Stage 2: Build Images**
```groovy
- Build backend: adithyakanneti0504/inventory-backend:latest
- Build frontend: adithyakanneti0504/inventory-frontend:latest-2
- Platform: linux/amd64 (EC2 compatible)
- Multi-stage builds for optimization
```

#### **Stage 3: Run Tests**
```groovy
- Unit tests (pytest)
- Integration tests
- Code coverage reports
```

#### **Stage 4: Push to Registry**
```groovy
- Docker Hub authentication
- Push latest tags
- Push build-specific tags (build-N)
```

#### **Stage 5: Deploy**
```groovy
- SSH to EC2 instances via bastion
- Pull latest images from Docker Hub
- Recreate containers with new images
- Verify health checks
```

### **GitHub Webhook Integration**

**Webhook URL:** `http://54.82.33.47:8080/github-webhook/`

**Trigger:** Push events to main branch

**Process:**
1. Developer pushes code to GitHub
2. GitHub sends webhook payload to Jenkins
3. Jenkins matches repository URL
4. Pipeline executes automatically
5. Build status reported back to GitHub

### **Docker Image Registry**

**Docker Hub Repository:**
- `adithyakanneti0504/inventory-backend:latest`
- `adithyakanneti0504/inventory-frontend:latest-2`

**Tagging Strategy:**
- `latest` - Most recent production build
- `build-N` - Specific build number for rollbacks

***

## 📊 Network Flow Diagrams

### **User Request Flow**

```
User Browser (http://3.94.146.75)
        ↓
Internet
        ↓
AWS Internet Gateway
        ↓
Frontend EC2 (Public Subnet)
        ↓
Nginx Container (Port 80)
        ↓
├─ "/" → React Static Files
└─ "/api/*" → Proxy to Backend
        ↓
Private Subnet (10.0.2.214:8000)
        ↓
Backend EC2 (FastAPI Container)
        ↓
PostgreSQL Container (Port 5432)
```

### **CI/CD Deployment Flow**

```
GitHub Repository
        ↓ (webhook)
Jenkins Server (Public Subnet)
        ↓ (SSH)
Frontend EC2 (10.0.1.111)
        ↓ (docker compose pull)
Docker Hub
        ↓ (docker compose up)
Updated Frontend Container
        ↓ (SSH via bastion)
Backend EC2 (10.0.2.214)
        ↓ (docker compose pull)
Docker Hub
        ↓ (docker compose up)
Updated Backend + Database
```

***

## Prerequisites

### **Development Requirements**
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- Git

### **AWS Requirements**
- AWS Account
- EC2 instances (Frontend, Backend, Jenkins)
- VPC with public/private subnets
- Security groups configured
- SSH key pair (sivera-pem.pem)

### **CI/CD Requirements**
- Jenkins server installed
- GitHub account and repository
- Docker Hub account
- Cerebras API key (for AI features)

***

## 📁 Project Structure

```
Smart-Inventory-Tracking/
├── backend/                          # Backend FastAPI application
│   ├── main.py                       # FastAPI application entry point
│   ├── Dockerfile                    # Backend container definition
│   ├── docker-compose.yml            # Backend services orchestration
│   ├── src/
│   │   ├── db/
│   │   │   ├── db_manager.py         # Database manager with connection pooling
│   │   │   └── migrations.sql        # Database schema and sample data
│   │   ├── models/
│   │   │   ├── product.py            # Product Pydantic models
│   │   │   ├── sale.py               # Sales Pydantic models
│   │   │   └── restock.py            # Restock Pydantic models
│   │   ├── routers/
│   │   │   ├── products.py           # Product API endpoints
│   │   │   ├── analytics.py          # Analytics API endpoints
│   │   │   └── ai_chat.py            # AI chat endpoints
│   │   ├── services/
│   │   │   ├── product_service.py    # Product business logic
│   │   │   ├── analytics_service.py  # Analytics & forecasting logic
│   │   │   ├── ai_agent.py           # AI agent with LangChain & Cerebras
│   │   │   ├── ai_tools/             # AI tools (single SQL tool)
│   │   │   │   └── sql_executor_tool.py
│   │   │   └── cache_service.py      # In-memory caching service
│   │   └── models/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── test_products.py          # Product service unit tests
│   │   └── test_analytics.py         # Analytics service unit tests
│   ├── pyproject.toml                # Backend dependencies
│   ├── .env                          # Environment variables
│   └── uv.lock                       # Dependency lock file
│
├── frontend/                         # React frontend application
│   ├── Dockerfile                    # Frontend container definition
│   ├── docker-compose.yml            # Frontend service orchestration
│   ├── nginx.conf                    # Nginx reverse proxy configuration
│   ├── src/
│   │   ├── components/
│   │   │   ├── ai/
│   │   │   │   └── ChatInterface.jsx    # AI chat interface
│   │   │   ├── alerts/
│   │   │   │   └── LowStockAlerts.jsx   # Low stock notifications
│   │   │   ├── analytics/
│   │   │   │   └── Analytics.jsx        # Analytics dashboard
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.jsx        # Main dashboard
│   │   │   │   └── KPICard.jsx          # KPI display component
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx           # Top navigation
│   │   │   │   ├── Layout.jsx           # Main layout wrapper
│   │   │   │   └── Sidebar.jsx          # Sidebar navigation
│   │   │   └── products/
│   │   │       └── ProductList.jsx      # Product management
│   │   ├── services/
│   │   │   └── api.js                  # HTTP client configuration
│   │   ├── stores/
│   │   │   ├── productStore.js         # Product state management (Zustand)
│   │   │   ├── analyticsStore.js       # Analytics state management
│   │   │   └── chatStore.js            # Chat state management
│   │   ├── App.jsx                     # Main React application
│   │   ├── main.jsx                    # React entry point
│   │   └── index.css                   # Global styles
│   ├── package.json                    # Frontend dependencies
│   ├── pnpm-lock.yaml                 # Dependency lock file
│   ├── vite.config.js                 # Vite configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   └── index.html                     # HTML template
│
├── Jenkinsfile                        # CI/CD pipeline definition
├── docker-compose.yml                 # Local development setup
├── RUN-BOTH.sh                       # Script to run both services locally
├── DEPLOYMENT.md                     # AWS deployment documentation
└── README.md                         # This file
```

***

## 🚀 Deployment Architecture

### **Production Deployment**

**Frontend (Public Subnet):**
```yaml
EC2: 3.94.146.75 (t2.micro)
├── Docker Container: inventory_frontend
│   ├── Nginx (Port 80)
│   ├── React Production Build
│   └── Reverse Proxy to Backend
└── docker-compose.yml
```

**Backend (Private Subnet):**
```yaml
EC2: 10.0.2.214 (t2.small)
├── Docker Container: inventory_backend
│   ├── FastAPI (Port 8000)
│   ├── LangChain AI Agent
│   └── Cerebras LLM Integration
└── Docker Container: inventory_postgres
    ├── PostgreSQL 15 (Port 5432)
    ├── Persistent Volume
    └── Automated Migrations
```

**Jenkins (Public Subnet):**
```yaml
EC2: 54.82.33.47 (t2.medium)
├── Jenkins Server (Port 8080)
├── Docker Engine
├── Pipeline Jobs
└── GitHub Webhook Integration
```

### **Security Best Practices**

1. **Network Isolation:**
   - Backend has NO public IP
   - Database only accessible within private subnet
   - SSH access via bastion host pattern

2. **API Security:**
   - Backend only accessible from frontend subnet
   - CORS configured for frontend domain
   - Nginx reverse proxy hides backend

3. **Secrets Management:**
   - Environment variables in `.env` files
   - Docker Hub credentials in Jenkins
   - SSH keys for EC2 access
   - API keys for Cerebras AI

***

## 🔧 Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/adiabb05-1317/Smart-Inventory-Tracking.git
cd Smart-Inventory-Tracking
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start PostgreSQL

```bash
docker-compose up -d
```

### 4. Run Migrations

```bash
./run_migrations.sh
```

### 5. Start Backend

```bash
cd backend
uv pip install -e .
python main.py
```

### 6. Start Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

**Local URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

***

## 🌐 Production URLs

- **Application:** http://3.94.146.75
- **API Health:** http://3.94.146.75/health
- **API Docs:** http://3.94.146.75/docs
- **Jenkins:** http://54.82.33.47:8080

---

## 📊 Monitoring & Maintenance

### **Health Checks**

```bash
# Frontend health
curl http://3.94.146.75/health

# Backend health  
curl http://3.94.146.75/api/health

# Database connection
ssh ubuntu@3.94.146.75
ssh ubuntu@10.0.2.214
docker exec -it inventory_postgres psql -U kubo_user -d inventory_db
```

### **View Logs**

```bash
# Frontend logs
ssh ubuntu@3.94.146.75
cd ~/inventory-frontend
docker compose logs -f

# Backend logs
ssh ubuntu@10.0.2.214
cd ~/inventory-backend
docker compose logs -f backend

# Database logs
docker compose logs -f postgres
```

### **Jenkins Pipeline Monitoring**

- Build history: http://54.82.33.47:8080/job/Smart-Inventory-CICD/
- Console output: Click on build number → Console Output
- Webhook deliveries: GitHub → Settings → Webhooks

***

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific tests
pytest tests/test_products.py -v
pytest tests/test_analytics.py -v
```

***

## 📚 API Documentation

Full API documentation available at:
- **Swagger UI:** http://3.94.146.75/docs
- **ReDoc:** http://3.94.146.75/redoc
