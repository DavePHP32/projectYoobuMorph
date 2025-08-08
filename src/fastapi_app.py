from fastapi import FastAPI
from pathlib import Path
import json

from routes import health, images, admin

app = FastAPI(
    title="YoobuMorph API",
    description="API for processing and uploading images to Azure Storage",
    version="1.0.0"
)

def load_azure_config():
    """Load Azure configuration from config file"""
    config_path = Path("config/yoobumorph_config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('azure_storage', {})

def setup_routes():
    """Setup and configure all routes"""
    # Load Azure configuration
    azure_config = load_azure_config()
    connection_string = azure_config.get('connection_string')
    container_name = azure_config.get('container_name', 'images')
    
    # Validate Azure configuration
    if not connection_string:
        raise ValueError("Azure connection string not found in configuration")
    
    # Configure routes with Azure settings
    health.set_azure_config(connection_string, container_name)
    images.set_azure_config(connection_string, container_name)
    admin.set_azure_config(connection_string, container_name)
    
    # Include routers
    app.include_router(health.router)
    app.include_router(images.router)
    app.include_router(admin.router)

# Setup routes on startup
setup_routes()

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to YoobuMorph API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "images": "/images"
        }
    }