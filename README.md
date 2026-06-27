# ClipoAI

**Enterprise AI Video Processing Platform** — Transform long-form videos into publish-ready short-form content using intelligent AI agents.

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Make](https://gnuwin32.sourceforge.net/packages/make.htm) (optional, for shortcuts)

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd ClipoAI

# Copy environment template
cp .env.example .env

# Edit .env with your secrets (JWT keys, YouTube API key, etc.)
```

### 2. Start Everything

```bash
# With Make
make up-build

# Without Make
docker compose up -d --build
```

### 3. Access Services

| Service | URL |
|---------|-----|
| **App** (via Nginx) | http://localhost |
| **Frontend** (direct) | http://localhost:5173 |
| **Backend API** | http://localhost:8080 |
| **API Docs** | http://localhost/api/docs |
| **MinIO Console** | http://localhost:9001 |
| **Grafana** | http://localhost:3000 |
| **Prometheus** | http://localhost:9090 |

### 4. Run Migrations

```bash
make migrate
```

### 5. Seed Database

```bash
make seed
```

## Development

```bash
make help          # Show all available commands
make logs          # Tail all logs
make logs-backend  # Tail backend logs
make test          # Run tests
make lint          # Lint backend code
make shell-backend # Open backend shell
make shell-db      # Open psql shell
```

## Architecture

```
frontend/    → React + TypeScript + TailwindCSS (Vite)
backend/     → FastAPI + SQLAlchemy + Alembic (Python)
infra/       → Nginx, Prometheus, Grafana, Loki configs
docs/        → Project documentation
scripts/     → Development utilities
tests/       → Test suites
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, TailwindCSS, Shadcn UI, TanStack Query |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Vector DB | Qdrant |
| Object Storage | MinIO (S3-compatible) |
| Monitoring | Prometheus, Grafana, Loki |
| Reverse Proxy | Nginx |
| Containerization | Docker, Docker Compose |

## License

Private — All rights reserved.
