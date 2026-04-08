import os
import sys
from datetime import datetime

# Add the backend directory to the sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app
try:
    from main import app as fastapi_app
except ImportError as e:
    raise ImportError(f"Could not import the FastAPI app: {e}")

# Passenger expects a WSGI application named `application`.
# FastAPI is ASGI, so we wrap it with a2wsgi.
try:
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(fastapi_app)
except ImportError:
    # Log the error to a file for debugging
    with open('passenger_error.log', 'a') as f:
        f.write(f"[{datetime.now()}] a2wsgi not installed. Install with: pip install a2wsgi\n")
    
    # Fallback to an error if a2wsgi is not installed
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = b"The a2wsgi library is not installed. Please install it with: pip install a2wsgi"
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
except Exception as e:
    with open('passenger_error.log', 'a') as f:
        import traceback
        f.write(f"[{datetime.now()}] Startup error: {str(e)}\n{traceback.format_exc()}\n")
    raise
