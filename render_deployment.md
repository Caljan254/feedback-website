# Deployment Plan: Hosting on Render

This plan outlines the steps to host the SEKU Feedback Management System on Render for testing purposes. We will use a **Unified Web Service** approach where the FastAPI backend serves the frontend static files.

## 1. Backend Modifications
- **Update `backend/requirements.txt`**: Add `psycopg2-binary` for PostgreSQL support (Render's default) and `gunicorn` for production serving.
- **Modify `backend/config.py`**: Ensure the app can handle Render's `DATABASE_URL` format and the `postgres://` vs `postgresql://` discrepancy.
- **Check `backend/main.py`**: Verify static file serving logic works on Render's Linux environment.

## 2. Render Configuration
- **Create `render.yaml`**: This file will define the service architecture, including the build and start commands.
  - **Build Command**: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
  - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker backend.main:app` (or similar)
- **Database**: We will recommend using a Render Free PostgreSQL instance.

## 3. Environment Variables
The following environment variables will be configured in Render:
- `DATABASE_URL`: Automatically provided by Render's PostgreSQL.
- `JWT_SECRET_KEY`: A secure random string.
- `FRONTEND_URL`: Set to the Render app URL (e.g., `https://seku-feedback.onrender.com`).
- `PYTHON_VERSION`: `3.10.0` or higher.

## 4. Execution Steps
1. [ ] Update `backend/requirements.txt`
2. [ ] Update `backend/config.py`
3. [ ] Create `render.yaml` in the root directory.
4. [ ] Create `Procfile` (alternative to render.yaml start command).
