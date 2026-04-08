from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from auth import get_current_user
from routes import router
from database import Base, engine
from models import User
from config import Config
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create DB tables with safety catch for production/test environments
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(f"Database initialization warning: {e}")
    # We continue so the API can at least start and serve a health check


app = FastAPI(title="Feedback Portal API")

# Request logger for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Standard CORS Middleware (Ordered first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



# Include all routes under /api
app.include_router(router, prefix="/api")

# Define static directories based on actual project structure
# When running via passenger_wsgi.py in root, paths are relative to root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
FRONTEND_SRC_JS = os.path.join(BASE_DIR, "frontend", "src", "js")

# Mount assets and other static folders if they exist
if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

# CRITICAL: Mount src carefully. The HTML expects ../../js from pages.
# If page is at /src/components/pages/home.html, it expects /src/js
# So we mount components separately OR we mount a combined src.
if os.path.exists(os.path.join(FRONTEND_DIST, "src")):
    app.mount("/src/components", StaticFiles(directory=os.path.join(FRONTEND_DIST, "src", "components")), name="components")

# Mount the JS source directory directly since dist might be missing it
if os.path.exists(FRONTEND_SRC_JS):
    app.mount("/src/js", StaticFiles(directory=FRONTEND_SRC_JS), name="js")
elif os.path.exists(os.path.join(FRONTEND_DIST, "js")):
    app.mount("/src/js", StaticFiles(directory=os.path.join(FRONTEND_DIST, "js")), name="js")

if os.path.exists(os.path.join(FRONTEND_DIST, "public")):
    app.mount("/public", StaticFiles(directory=os.path.join(FRONTEND_DIST, "public")), name="public")
if os.path.exists(os.path.join(FRONTEND_DIST, "departments")):
    app.mount("/departments", StaticFiles(directory=os.path.join(FRONTEND_DIST, "departments")), name="departments")
if os.path.exists(os.path.join(FRONTEND_DIST, "uploads")):
    app.mount("/uploads", StaticFiles(directory=os.path.join(FRONTEND_DIST, "uploads")), name="uploads")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Serve static HTML files from frontend/dist
@app.get("/")
async def serve_home():
    path = os.path.join(FRONTEND_DIST, "index.html")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Index.html not found. Please run 'npm run build' in frontend.</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading index: {str(e)}</h1>", status_code=500)

@app.get("/login")
async def serve_login():
    path = os.path.join(FRONTEND_DIST, "src", "components", "pages", "login.html")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Login page not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

@app.get("/admin")
async def serve_admin(current_user: User = Depends(get_current_user)):
    path = os.path.join(FRONTEND_DIST, "src", "components", "pages", "admin.html")
    try:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Admin page not found</h1>", status_code=404)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving admin page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )