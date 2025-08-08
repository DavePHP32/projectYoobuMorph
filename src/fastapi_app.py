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
    """Load Azure configuration from config file or environment variables"""
    import os
    
    # Try environment variables first (for production)
    connection_string = os.getenv('AZURE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_CONTAINER_NAME', 'processed-images')
    
    if connection_string:
        return {
            'connection_string': connection_string,
            'container_name': container_name
        }
    
    # Fallback to config file (for local development)
    config_path = Path("config/yoobumorph_config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('azure_storage', {})
    
    return {}

def setup_routes():
    """Setup and configure all routes"""
    # Load Azure configuration
    azure_config = load_azure_config()
    connection_string = azure_config.get('connection_string')
    container_name = azure_config.get('container_name', 'processed-images')
    
    # Configure routes with Azure settings (if available)
    if connection_string:
        try:
            health.set_azure_config(connection_string, container_name)
            images.set_azure_config(connection_string, container_name)
            admin.set_azure_config(connection_string, container_name)
            print(f"✅ Azure Storage configured successfully for container: {container_name}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to configure Azure Storage: {str(e)}")
    else:
        print("⚠️ Warning: Azure connection string not found. Some endpoints may not work.")
    
    # Include routers (always include them)
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