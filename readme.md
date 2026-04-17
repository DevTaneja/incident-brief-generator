# Incident Brief Generator

Production-ready incident analysis system that correlates logs, metrics, and issue tracking with AI-powered insights.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Services](#services)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Incident Brief Generator automates the process of gathering and correlating data from multiple observability and tracking systems during production incidents. It eliminates manual data collection by providing a unified interface to:

- Retrieve logs from **Splunk** using `requestId` correlation
- Fetch performance metrics from **New Relic**
- Search **Jira** for similar past issues using LLM-extracted keywords
- Generate AI-powered root cause analysis and recommendations
- Export structured reports in PDF or Markdown format

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Compose                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐      │
│   │   Backend    │   │   Frontend   │   │ Test Service │      │
│   │   :8000      │   │   :3000      │   │   :8001      │      │
│   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘      │
│          │                  │                   │               │
│          └──────────────────┼───────────────────┘               │
│                             │                                   │
│                     incident-network                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │      External Services    │
              │  - Splunk                 │
              │  - New Relic              │
              │  - Jira                   │
              │  - Groq (LLM)             │
              └───────────────────────────┘
```

### Technology Stack

| Component        | Technology               |
| ---------------- | ------------------------ |
| Backend          | FastAPI (Python 3.12)    |
| Frontend         | React + Vite             |
| Containerization | Docker + Docker Compose  |
| Logs             | Splunk (REST API)        |
| Metrics          | New Relic (GraphQL API)  |
| Issue Tracking   | Jira Cloud (REST API)    |
| LLM              | Groq API (Llama 3.3 70B) |
| PDF Generation   | ReportLab                |
| HTTP Client      | HTTPX                    |

---

## Prerequisites

### Required Software

- Docker Desktop 4.20+ (with Docker Compose)
- Git 2.40+

### Required Credentials

You will need valid credentials for the following services:

| Service   | Purpose       | Credentials Required                    |
| --------- | ------------- | --------------------------------------- |
| Splunk    | Log retrieval | API token, username, password, host URL |
| New Relic | Metrics       | API key, account ID, license key        |
| Jira      | Issue search  | Instance URL, email, API token          |
| Groq      | LLM analysis  | API key (free tier available)           |

> **Note:** A test service is included to generate sample data if you do not have access to production systems.

---

## Quick Start

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-organization/incident-brief-generator.git
cd incident-brief-generator
```

### Step 2 — Configure Environment Variables

Copy the example environment file and populate it with your credentials:

```bash
cp .env.example .env
```

See the [Configuration](#configuration) section for a full reference of required variables.

### Step 3 — Build and Run

```bash
docker-compose up -d --build
```

This builds the Docker images and starts all three services in detached mode.

### Step 4 — Access the Application

| Service      | URL                            | Purpose                              |
| ------------ | ------------------------------ | ------------------------------------ |
| Frontend UI  | http://localhost:3000          | Web interface for incident briefs    |
| Backend API  | http://localhost:8000          | REST API endpoint                    |
| API Docs     | http://localhost:8000/api/docs | Interactive Swagger documentation    |
| Test Service | http://localhost:8001          | Generate sample log data for testing |

### Step 5 — Generate a Test Incident (Optional)

To test without production data, trigger a sample error via the test service:

```bash
curl -X POST http://localhost:8001/force-error \
  -H "Content-Type: application/json" \
  -d '{"requestId": "test-001"}'
```

Use the returned `requestId` in the frontend to generate an incident brief.

### Step 6 — Stop Services

```bash
docker-compose down
```

To also remove volumes:

```bash
docker-compose down -v
```

---

## Configuration

### Environment Variables

Create a `.env` file in the root directory. The full reference is below.

```env
# ── Splunk ────────────────────────────────────────────────────────────────────
SPLUNK_HOST=host.docker.internal
SPLUNK_PORT=8089
SPLUNK_USERNAME=your_username
SPLUNK_PASSWORD=your_password
SPLUNK_API_TOKEN=your_hec_token
SPLUNK_HEC_URL=https://host.docker.internal:8088/services/collector

# ── New Relic ─────────────────────────────────────────────────────────────────
NEW_RELIC_LICENSE_KEY=your_license_key
NEW_RELIC_API_KEY=your_api_key
NEW_RELIC_ACCOUNT_ID=your_account_id
NEW_RELIC_CONFIG_PATH=/app/newrelic.ini

# ── Jira ──────────────────────────────────────────────────────────────────────
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=IBG

# ── Groq ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# ── Test Service ──────────────────────────────────────────────────────────────
ERROR_RATE=0.3
```

> **Important:** Use `host.docker.internal` instead of `localhost` when referencing services running on the host machine (e.g., a local Splunk instance). Cloud services (New Relic, Jira, Groq) use their standard public URLs. Never commit `.env` to version control.

---

## Services

### Backend API — Port 8000

FastAPI application responsible for data fetching, correlation, and LLM processing.

| Method | Endpoint                  | Description                                 |
| ------ | ------------------------- | ------------------------------------------- |
| `POST` | `/api/v1/generate-brief`  | Generate an incident brief from a requestId |
| `POST` | `/api/v1/download-report` | Download report as PDF or Markdown          |
| `GET`  | `/health`                 | Health check                                |
| `GET`  | `/api/docs`               | Swagger documentation                       |

### Frontend — Port 3000

React-based user interface providing:

- Input form for `requestId`, time range, and environment
- Structured display of the generated incident brief
- PDF and Markdown export buttons

### Test Service — Port 8001

Optional service for generating sample log data:

- Simulates API requests with a configurable error rate (default: 30%)
- Sends correlated logs to Splunk using `requestId`
- Provides a `/force-error` endpoint for deterministic error generation

---

## API Documentation

### Generate Incident Brief

**Request**

```bash
curl -X POST http://localhost:8000/api/v1/generate-brief \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "abc-123",
    "time_range": "1h",
    "environment": "prod"
  }'
```

**Response**

```json
{
  "request_id": "abc-123",
  "time_range": "1h",
  "environment": "prod",
  "generated_at": "2024-01-01T00:00:00Z",
  "summary": "Database connection timeout detected...",
  "errors_found": [],
  "total_logs": 5,
  "timeline": [],
  "suggested_next_steps": [],
  "success": true,
  "message": "Found 5 logs. New Relic: 10 transactions, 2 errors. Jira: 1 related issues"
}
```

### Download Report

**Request**

```bash
curl -X POST http://localhost:8000/api/v1/download-report \
  -H "Content-Type: application/json" \
  -d '{
    "brief": {},
    "format": "pdf"
  }'
```

**Response:** Binary file download (PDF or Markdown).

---

## Development

### Running Without Docker

**Backend**

```bash
cd backend
pip install -r requirements.txt
python run.py
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Test Service**

```bash
cd test-service
pip install -r requirements.txt
python -c "from app import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001)"
```

### Project Structure

```
incident-brief-generator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── test-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── newrelic.ini
├── docker-compose.yml
├── .env.example
└── README.md
```

### Running Tests

```bash
# Backend
cd backend
python tests/test_splunk_search.py
python tests/test_jira.py
python tests/test_llm.py

# Frontend
cd frontend
npm test
```

---

## Deployment

### Production Checklist

Before deploying to production, ensure the following:

- **Remove the test service** — it is intended for development only
- **Enable HTTPS** — configure SSL certificates on the reverse proxy
- **Use secrets management** — do not pass credentials via plain environment files
- **Restrict CORS origins** — limit allowed origins to your production domain
- **Add rate limiting** — protect the API from abuse
- **Configure centralized logging** — aggregate logs from all containers
- **Set up health checks** — required for orchestration platforms (Kubernetes, ECS, etc.)

### Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Troubleshooting

### Splunk connection fails from inside Docker

**Cause:** Using `localhost` in `.env` resolves to the container itself, not the host machine.

**Fix:** Use `host.docker.internal` in your `.env`:

```env
SPLUNK_HOST=host.docker.internal
SPLUNK_HEC_URL=https://host.docker.internal:8088/services/collector
```

---

### Port 3000 or 8000 is already in use

**Fix:** Update the host-side port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3001:80" # Frontend
  - "8002:8000" # Backend
```

---

### New Relic shows no transaction data

**Fix:**

1. Confirm `NEW_RELIC_LICENSE_KEY` is set correctly in `.env`
2. Verify `newrelic.ini` contains `license_key = ${NEW_RELIC_LICENSE_KEY}`
3. Allow a few minutes for data to appear in the New Relic UI after first run

---

### Jira search returns no results

**Fix:**

1. Verify `JIRA_PROJECT_KEY` matches your actual project key
2. Confirm the issues contain the extracted keywords in their summary or description fields
3. Ensure the API token has `browse projects` and `search` permissions

---

### Viewing service logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs test-service

# Stream logs in real time
docker-compose logs -f backend
```

---

### Rebuilding after code changes

```bash
docker-compose up -d --build
```

### Full cleanup

```bash
docker-compose down -v
docker system prune -a
```

---

## Known Limitations

- Splunk search uses a fixed 2-second wait instead of polling — acceptable for small-scale deployments but may miss results under heavy load
- New Relic time range conversion only supports `m`, `h`, and `d` suffixes
- No built-in retry logic for external API failures
- The test service requires a locally running Splunk instance for log storage

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

Specify your license here.

---

## Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — high-performance Python web framework
- [Groq](https://groq.com/) — fast LLM inference API
- Splunk, New Relic, and Atlassian for their well-documented APIs
