Incident Brief Generator
Production-ready incident analysis system correlating logs, metrics, and issue tracking with AI-powered insights.
Table of Contents
Overview

Architecture

Prerequisites

Quick Start

Configuration

Services

API Documentation

Development

Deployment

Troubleshooting

Overview
The Incident Brief Generator automates the process of gathering and correlating data from multiple observability and tracking systems during production incidents. It eliminates manual data collection by providing a unified interface to:

Retrieve logs from Splunk using requestId correlation

Fetch performance metrics from New Relic

Search Jira for similar past issues using LLM-extracted keywords

Generate AI-powered root cause analysis and recommendations

Export structured reports in PDF or Markdown format

Architecture
text
┌─────────────────────────────────────────────────────────────────┐
│ Docker Compose │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Backend │ │ Frontend │ │ Test Service │ │
│ │ :8000 │ │ :3000 │ │ :8001 │ │
│ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │
│ │ │ │ │
│ └─────────────────┼─────────────────┘ │
│ │ │
│ incident-network │
│ │
└─────────────────────────────────────────────────────────────────┘
│
↓
┌─────────────────────────┐
│ External Services │
│ - Splunk │
│ - New Relic │
│ - Jira │
│ - Groq (LLM) │
└─────────────────────────┘
Technology Stack
Component Technology
Backend Framework FastAPI (Python 3.12)
Frontend React + Vite
Containerization Docker + Docker Compose
Logs Splunk (via REST API)
Metrics New Relic (via GraphQL API)
Issue Tracking Jira Cloud (via REST API)
LLM Groq API (Llama 3.3 70B)
PDF Generation ReportLab
HTTP Client HTTPX
Prerequisites
Before running the application, ensure you have:

Required Software
Docker Desktop 4.20+ (with Docker Compose)

Git 2.40+

Required Accounts and Credentials
You will need valid credentials for the following services:

Service Purpose Credentials Needed
Splunk Log retrieval API token, username, password, host URL
New Relic Metrics retrieval API key, account ID, license key
Jira Issue search Instance URL, email, API token
Groq LLM analysis API key (free tier available)
Note: A test service is included to generate sample data if you do not have access to production systems.

Quick Start
Step 1: Clone the Repository
bash
git clone https://github.com/your-organization/incident-brief-generator.git
cd incident-brief-generator
Step 2: Configure Environment Variables
Copy the example environment file and edit with your credentials:

bash
cp .env.example .env
Edit .env with your actual credentials (see Configuration section below).

Step 3: Build and Run
bash
docker-compose up -d --build
This command builds the Docker images and starts all three services in detached mode.

Step 4: Access the Application
Service URL Purpose
Frontend UI http://localhost:3000 Web interface for generating incident briefs
Backend API http://localhost:8000 REST API endpoint
API Documentation http://localhost:8000/api/docs Interactive Swagger documentation
Test Service http://localhost:8001 Generate sample log data for testing
Step 5: Generate a Test Incident (Optional)
If you want to test without production data:

bash
curl -X POST http://localhost:8001/force-error \
 -H "Content-Type: application/json" \
 -d '{"requestId":"test-001"}'
Then use the returned requestId in the frontend to generate an incident brief.

Step 6: Stop Services
bash
docker-compose down
To remove volumes as well:

bash
docker-compose down -v
Configuration
Environment Variables (.env)
Create a .env file in the root directory with the following variables:

env

# ============================================

# SPLUNK CONFIGURATION

# ============================================

SPLUNK_HOST=host.docker.internal
SPLUNK_PORT=8089
SPLUNK_USERNAME=your_username
SPLUNK_PASSWORD=your_password
SPLUNK_API_TOKEN=your_hec_token
SPLUNK_HEC_URL=https://host.docker.internal:8088/services/collector

# ============================================

# NEW RELIC CONFIGURATION

# ============================================

NEW_RELIC_LICENSE_KEY=your_license_key
NEW_RELIC_API_KEY=your_api_key
NEW_RELIC_ACCOUNT_ID=your_account_id
NEW_RELIC_CONFIG_PATH=/app/newrelic.ini

# ============================================

# JIRA CONFIGURATION

# ============================================

JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=IBG

# ============================================

# GROQ LLM CONFIGURATION

# ============================================

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# ============================================

# TEST SERVICE CONFIGURATION

# ============================================

ERROR_RATE=0.3
Important Notes for Docker
Use host.docker.internal instead of localhost when referring to services running on the host machine (e.g., local Splunk instance)

Cloud services (New Relic, Jira, Groq) use their standard URLs

Never commit the .env file to version control

Services

1. Backend API (Port 8000)
   FastAPI application handling all data fetching, correlation, and LLM processing.

Key Endpoints:

Method Endpoint Description
POST /api/v1/generate-brief Generate incident brief from requestId
POST /api/v1/download-report Download report as PDF or Markdown
GET /health Health check
GET /api/docs Swagger documentation 2. Frontend (Port 3000)
React-based user interface providing:

Input form for requestId, time range, and environment

Structured display of incident brief

PDF and Markdown download buttons

3. Test Service (Port 8001)
   Optional service for generating sample log data:

Simulates API requests with configurable error rate (default 30%)

Sends logs to Splunk with requestId correlation

Provides /force-error endpoint for deterministic error generation

API Documentation
Generate Incident Brief
Request:

bash
curl -X POST http://localhost:8000/api/v1/generate-brief \
 -H "Content-Type: application/json" \
 -d '{
"request_id": "abc-123",
"time_range": "1h",
"environment": "prod"
}'
Response:

json
{
"request_id": "abc-123",
"time_range": "1h",
"environment": "prod",
"generated_at": "2024-01-01T00:00:00Z",
"summary": "Database connection timeout detected...",
"errors_found": [...],
"total_logs": 5,
"timeline": [...],
"suggested_next_steps": [...],
"success": true,
"message": "Found 5 logs. New Relic: 10 transactions, 2 errors. Jira: 1 related issues"
}
Download Report
Request:

bash
curl -X POST http://localhost:8000/api/v1/download-report \
 -H "Content-Type: application/json" \
 -d '{
"brief": {...},
"format": "pdf"
}'
Response: Binary file download (PDF or Markdown)

Development
Running Without Docker
Backend:

bash
cd backend
pip install -r requirements.txt
python run.py
Frontend:

bash
cd frontend
npm install
npm run dev
Test Service:

bash
cd test-service
pip install -r requirements.txt
python -c "from app import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001)"
Project Structure
text
incident-brief-generator/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ ├── core/
│ │ ├── integrations/
│ │ ├── models/
│ │ └── services/
│ ├── requirements.txt
│ └── Dockerfile
├── frontend/
│ ├── src/
│ ├── package.json
│ ├── Dockerfile
│ └── nginx.conf
├── test-service/
│ ├── app.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── newrelic.ini
├── docker-compose.yml
├── .env.example
└── README.md
Running Tests
bash

# Backend tests

cd backend
python tests/test_splunk_search.py
python tests/test_jira.py
python tests/test_llm.py

# Frontend tests

cd frontend
npm test
Deployment
Production Considerations
Before deploying to production:

Remove Test Service - The test service is for development only

Enable HTTPS - Configure SSL certificates

Set Secure Environment Variables - Use secrets management

Configure Proper CORS - Restrict allowed origins

Add Rate Limiting - Prevent API abuse

Set Up Logging - Centralized log aggregation

Configure Health Checks - For orchestration platforms

Docker Production Build
bash
docker-compose -f docker-compose.prod.yml up -d --build
Troubleshooting
Splunk Connection Failed
Issue: Cannot connect to Splunk from Docker container

Solution: Use host.docker.internal instead of localhost in .env:

env
SPLUNK_HOST=host.docker.internal
SPLUNK_HEC_URL=https://host.docker.internal:8088/services/collector
Port Conflicts
Issue: Port 3000 or 8000 already in use

Solution: Change ports in docker-compose.yml:

yaml
ports:

- "3001:80" # instead of 3000
- "8002:8000" # instead of 8000
  New Relic Not Receiving Data
  Issue: No transactions appear in New Relic

Solution:

Verify license key is correct

Check that NEW_RELIC_LICENSE_KEY is set in .env

Ensure newrelic.ini has license_key = ${NEW_RELIC_LICENSE_KEY}

Jira Search Returns No Results
Issue: No issues found even with valid keywords

Solution:

Verify Jira project key is correct

Check that issues contain the keywords in summary or description

Ensure API token has search permissions

View Service Logs
bash

# View all logs

docker-compose logs

# View specific service

docker-compose logs backend
docker-compose logs frontend
docker-compose logs test-service

# Follow logs in real-time

docker-compose logs -f backend
Rebuild After Code Changes
bash
docker-compose up -d --build
Complete Cleanup
bash
docker-compose down -v
docker system prune -a
Known Limitations
Splunk search uses fixed 2-second wait instead of polling (acceptable for small-scale deployments)

New Relic time range conversion supports only m/h/d units

No built-in retry logic for API failures

Test service requires local Splunk for log storage

Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Open a Pull Request

License
[Specify your license here]

Support
For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

Acknowledgments
FastAPI for the excellent web framework

Groq for providing fast LLM inference

Splunk, New Relic, and Atlassian for their APIs

text

---

This README is production-ready, professional, and contains all necessary information for another developer to successfully run the project.
