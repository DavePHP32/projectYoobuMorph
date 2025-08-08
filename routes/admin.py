"""
Admin routes for YoobuMorph FastAPI application
==============================================

This module contains administrative endpoints for managing Azure Storage containers
and other administrative tasks.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from utils.azure_storage import AzureStorageManager

router = APIRouter(prefix="/admin", tags=["admin"])

# Global Azure Storage Manager
azure_storage_manager: AzureStorageManager = None

def set_azure_config(connection_string: str, container_name: str):
    """Set Azure configuration for admin operations"""
    global azure_storage_manager
    azure_storage_manager = AzureStorageManager(connection_string, container_name)

@router.delete("/container")
def delete_container() -> Dict[str, Any]:
    """Delete the current container"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
        
        container_name = azure_storage_manager.container_name
        
        # Check if container exists
        if not azure_storage_manager.container_client.exists():
            return {
                "message": f"Container '{container_name}' does not exist",
                "container_name": container_name,
                "action": "delete",
                "status": "not_found"
            }
        
        # Delete container
        azure_storage_manager.container_client.delete_container()
        
        return {
            "message": f"Container '{container_name}' deleted successfully",
            "container_name": container_name,
            "action": "delete",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete container: {str(e)}")

@router.post("/container")
def create_container(public_access: bool = True) -> Dict[str, Any]:
    """Create the container with specified access level"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
        
        container_name = azure_storage_manager.container_name
        
        # Check if container already exists
        if azure_storage_manager.container_client.exists():
            return {
                "message": f"Container '{container_name}' already exists",
                "container_name": container_name,
                "action": "create",
                "status": "already_exists",
                "public_access": public_access
            }
        
        # Create container with specified access level
        if public_access:
            from azure.storage.blob import PublicAccess
            azure_storage_manager.container_client.create_container(public_access=PublicAccess.Blob)
            access_type = "public"
        else:
            azure_storage_manager.container_client.create_container()
            access_type = "private"
        
        return {
            "message": f"Container '{container_name}' created successfully with {access_type} access",
            "container_name": container_name,
            "action": "create",
            "status": "success",
            "public_access": public_access,
            "access_type": access_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create container: {str(e)}")

@router.post("/container/recreate")
def recreate_container(public_access: bool = True) -> Dict[str, Any]:
    """Delete and recreate the container with specified access level"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
        
        container_name = azure_storage_manager.container_name
        
        # Delete container if it exists
        if azure_storage_manager.container_client.exists():
            azure_storage_manager.container_client.delete_container()
        
        # Create container with specified access level
        if public_access:
            from azure.storage.blob import PublicAccess
            azure_storage_manager.container_client.create_container(public_access=PublicAccess.Blob)
            access_type = "public"
        else:
            azure_storage_manager.container_client.create_container()
            access_type = "private"
        
        return {
            "message": f"Container '{container_name}' recreated successfully with {access_type} access",
            "container_name": container_name,
            "action": "recreate",
            "status": "success",
            "public_access": public_access,
            "access_type": access_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recreate container: {str(e)}")

@router.get("/container/status")
def get_container_status() -> Dict[str, Any]:
    """Get the current status of the container"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
        
        container_name = azure_storage_manager.container_name
        exists = azure_storage_manager.container_client.exists()
        
        if exists:
            # Get container properties
            properties = azure_storage_manager.container_client.get_container_properties()
            public_access = properties.public_access
            
            return {
                "container_name": container_name,
                "exists": True,
                "public_access": str(public_access),
                "last_modified": str(properties.last_modified),
                "etag": properties.etag
            }
        else:
            return {
                "container_name": container_name,
                "exists": False,
                "public_access": None,
                "last_modified": None,
                "etag": None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get container status: {str(e)}")

@router.get("/blobs")
def list_blobs(prefix: str = None) -> Dict[str, Any]:
    """List all blobs in the container"""
    try:
        if not azure_storage_manager:
            raise HTTPException(status_code=500, detail="Azure configuration not set")
        
        blobs = azure_storage_manager.list_blobs(prefix)
        
        return {
            "container_name": azure_storage_manager.container_name,
            "blob_count": len(blobs),
            "blobs": blobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blobs: {str(e)}")
