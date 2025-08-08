"""
Health check routes for YoobuMorph FastAPI application
====================================================

This module contains health check endpoints to verify the application status
and Azure Storage connection.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from utils.azure_storage import AzureStorageManager

router = APIRouter(prefix="/health", tags=["health"])

# Global Azure Storage Manager
azure_storage_manager: AzureStorageManager = None

def set_azure_config(connection_string: str, container_name: str):
    """Set Azure configuration for health checks"""
    global azure_storage_manager
    azure_storage_manager = AzureStorageManager(connection_string, container_name)

@router.get("/")
def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify Azure Storage connection"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
            
        connection_status = azure_storage_manager.test_connection()
        
        if connection_status["status"] == "connected":
            return {
                "status": "healthy",
                "azure_storage": "connected",
                "container_name": azure_storage_manager.container_name,
                "account_name": connection_status["account_name"],
                "container_exists": connection_status["container_exists"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Azure Storage connection failed: {connection_status['error']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Azure Storage connection failed: {str(e)}")

@router.get("/ping")
def ping() -> Dict[str, str]:
    """Simple ping endpoint"""
    return {"message": "pong"}
