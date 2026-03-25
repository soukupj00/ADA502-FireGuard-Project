# ADA502 FireGuard Project - Your Fireguard

FireGuard is a fire risk calculation system designed to monitor, compute, and visualize fire risks based on weather data. The system operates as a monorepo containing three distinct services: a Backend API, a Frontend User Interface, and an Intelligence System for background data processing.

## Architecture Overview

The system follows a microservices architecture:

1.  **Frontend (React + Vite):** A web interface for users to view fire risk data.
2.  **Backend (FastAPI):** A REST API that serves data to the frontend and manages user requests.
3.  **Intelligence System (Python Worker):** A background service that periodically fetches weather data from MET.no, computes Fire Risk Indices (FRCM), and updates the database.
4.  **Database (PostgreSQL):** A shared database used by the Backend (Reader) and Intelligence System (Writer).
5.  **Keycloak:** An identity and access management solution for user authentication.
6.  **Redis:** An in-memory data store used for caching and message broking.

## Project Structure

* **backend/**: Contains the FastAPI application code, database models, and API routers.
* **frontend/**: Contains the React application source code and Nginx configuration.
* **intelligence-system/**: Contains the background worker logic and the Fire Risk Calculation Model (FRCM).
* **.github/workflows/ci.yml**: GitHub Actions configuration for CI/CD.
* **.pre-commit-config.yaml**: Pre-commit hooks configuration.
* **docker-compose.yml**: Configuration for the local development environment.
* **docker-compose.prod.yml**: Configuration for the production environment (NREC).

## Prerequisites

To run this project, you need the following tools installed:

* **Docker & Docker Compose** (Recommended for all environments)
* **Python 3.12+** and **uv** (for local backend/intelligence development)
* **Node.js 20+** (for local frontend development)
* **pre-commit** (for code quality)

## Getting Started (Development)

The recommended way to run the project locally is using Docker Compose. This spins up the database, backend, frontend, and intelligence worker in a synchronized environment with hot-reloading enabled.

### 1. Using Docker Compose

1.  Clone the repository:
    ```bash
    git clone git@github.com:soukupj00/ADA502-FireGuard-Project.git
    cd ADA502-FireGuard-Project
    ```

2.  Start the services:
    ```bash
    docker compose up --build (optional -d for detached mode)
    ```

3.  Access the application:
    * **Frontend:** http://localhost:5173
    * **Backend API Docs:** http://localhost:8000/api/docs
    * **Keycloak Admin Console:** http://localhost:8080/auth/admin (User: `admin`, Password: `admin`)
    * **Application Database:** localhost:5433 (User: `user`, Password: `password`)
    * **Keycloak Database:** localhost:5434 (User: `keycloak_user`, Password: `keycloak_password`)
    * **Redis:** localhost:6379

### 2. Manual Setup (Running Services Individually)

If you prefer to run services natively on your machine without Docker, follow these steps. Note that you must have a PostgreSQL database, Redis, and Keycloak running separately.

#### Backend
1.  Navigate to `backend/`.
2.  Install dependencies:
    ```bash
    uv sync
    ```
3.  Run the server:
    ```bash
    uv run fastapi dev src/app/main.py
    ```

#### Frontend
1.  Navigate to `frontend/`.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

#### Intelligence System
1.  Navigate to `intelligence-system/`.
2.  Install dependencies:
    ```bash
    uv sync
    ```
3.  Run the worker:
    ```bash
    uv run python src/main.py
    ```

## Testing, Linting and CI/CD

The project enforces code quality through automated tests, linting, and pre-commit hooks. The CI/CD pipeline is configured using GitHub Actions and automatically runs on every push and pull request to the `main` branch.

### Pre-commit Hooks

This project uses `pre-commit` to automatically lint and format code before each commit. To set it up:

1.  Install `pre-commit`:
    ```bash
    pip install pre-commit
    ```
2.  Install the hooks:
    ```bash
    pre-commit install
    ```

Now, `ruff` (for Python) and `prettier`/`eslint` (for the frontend) will run automatically on staged files before you commit.

### CI/CD

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and consists of three jobs:

1.  **Backend CI:** Lints, tests, and builds the backend Docker image.
2.  **Intelligence System CI:** Lints, tests, and builds the intelligence system Docker image.
3.  **Frontend CI:** Lints, type-checks, and builds the frontend application.

## Deployment (NREC)

The application is deployed on the NREC cloud platform using Docker Compose in production mode.

### Production Environment Differences
* **Nginx Reverse Proxy:** The frontend container builds a static site served by Nginx. Nginx also proxies API requests (from `/api`) to the backend container, eliminating CORS issues.
* **Database Persistence:** Data is stored in a Docker volume to persist across restarts.
* **Security:** Production uses strict environment variables and does not expose internal ports (like 8000) to the public internet.

### Deployment Workflow
1.  SSH into the NREC instance:
    ```bash
    ssh ubuntu@158.37.63.48
    ```

2.  Navigate to the project directory:
    ```bash
    cd ADA502-FireGuard-Project
    ```

3.  Pull the latest changes:
    ```bash
    git pull origin main
    ```

4.  Rebuild and restart the services:
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build
    ```

### Viewing Logs
To monitor the services on the production server:

* **All services:**
    ```bash
    docker compose -f docker-compose.prod.yml logs -f
    ```
* **Specific service (e.g., Intelligence System):**
    ```bash
    docker compose -f docker-compose.prod.yml logs -f intelligence
    ```

## Troubleshooting

**Port Conflicts:**
If you cannot start the containers, ensure ports `5432` (Postgres), `8000` (Backend), or `5173` (Frontend) are not being used by other applications on your machine.

**Database Connection Errors:**
Ensure the `DATABASE_URL` environment variable matches the credentials defined in the `docker-compose.yml` file. In development, the hostname is `localhost` (if running locally) or `db` (if running inside Docker).
