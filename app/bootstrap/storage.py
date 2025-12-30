import os
from fastapi.staticfiles import StaticFiles

def mount_storage(app):
    """Mount public storage directory for static file serving"""
    public_path = os.path.join(os.getcwd(), "storage", "public")
    
    # Only mount if the directory exists
    if os.path.exists(public_path):
        app.mount("/storage", StaticFiles(directory=public_path), name="static")
