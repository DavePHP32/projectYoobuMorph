"""
Azure Storage utilities for YoobuMorph
=====================================

This module handles all Azure Blob Storage operations including
container management, file uploads, and connection management.
"""

from azure.storage.blob import BlobServiceClient, ContainerClient
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AzureStorageManager:
    """Manages Azure Blob Storage operations"""
    
    def __init__(self, connection_string: str, container_name: str = "processed-images"):
        """
        Initialize Azure Storage Manager
        
        Args:
            connection_string: Azure Storage connection string
            container_name: Name of the container to use
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = None
        self.container_client = None
        
        # Initialize connection
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the blob service client"""
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            logger.info(f"Azure Storage client initialized for container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage client: {str(e)}")
            raise
    
    def ensure_container_exists(self) -> bool:
        """
        Ensure the container exists, create it if it doesn't
        
        Returns:
            bool: True if container exists or was created successfully
        """
        try:
            if not self.container_client.exists():
                # Create container without public access (SAS will be used)
                self.container_client.create_container()
                logger.info(f"✅ Container '{self.container_name}' created (SAS URLs will be used)")
                return True
            else:
                logger.info(f"✅ Container '{self.container_name}' already exists")
                return True
        except Exception as e:
            logger.error(f"⚠️ Failed to create container '{self.container_name}': {str(e)}")
            return False
    
    def upload_file(self, local_path: Path, blob_name: str, generate_sas: bool = False) -> str:
        """
        Upload a file to Azure Blob Storage
        
        Args:
            local_path: Path to the local file
            blob_name: Name to give the blob in Azure
            generate_sas: Whether to generate a SAS token for the URL
            
        Returns:
            str: URL of the uploaded blob (with SAS token if requested)
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Ensure container exists before upload
            if not self.ensure_container_exists():
                raise Exception(f"Container '{self.container_name}' could not be created")
            
            # Get blob client and upload
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            with open(local_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
                
            # Set content type for web display
            from azure.storage.blob import ContentSettings
            blob_client.set_http_headers(content_settings=ContentSettings(
                content_type='image/jpeg',
                cache_control='public, max-age=31536000'
            ))
            
            logger.info(f"✅ File uploaded successfully: {blob_name}")
            
            # Return URL with or without SAS token
            if generate_sas:
                return self._generate_sas_url(blob_name)
            else:
                return blob_client.url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload file {blob_name}: {str(e)}")
            raise Exception(f"Failed to upload to Azure Blob Storage: {str(e)}")
    
    def _generate_sas_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Generate a SAS URL for a blob
        
        Args:
            blob_name: Name of the blob
            expiry_hours: Hours until the SAS token expires
            
        Returns:
            str: URL with SAS token
        """
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        # Extract account key from connection string
        import re
        account_key_match = re.search(r'AccountKey=([^;]+)', self.connection_string)
        if not account_key_match:
            raise Exception("Could not extract account key from connection string")
        
        account_key = account_key_match.group(1)
        
        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        # Construct URL with SAS token
        blob_url = self.get_blob_url(blob_name)
        return f"{blob_url}?{sas_token}"
    
    def list_blobs(self, prefix: Optional[str] = None) -> list:
        """
        List blobs in the container
        
        Args:
            prefix: Optional prefix to filter blobs
            
        Returns:
            list: List of blob names
        """
        try:
            blobs = []
            for blob in self.container_client.list_blobs(name_starts_with=prefix):
                blobs.append(blob.name)
            return blobs
        except Exception as e:
            logger.error(f"Failed to list blobs: {str(e)}")
            return []
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from the container
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"✅ Blob deleted successfully: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete blob {blob_name}: {str(e)}")
            return False
    
    def get_blob_url(self, blob_name: str) -> str:
        """
        Get the URL of a blob
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            str: URL of the blob
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        return blob_client.url
    
    def test_connection(self) -> dict:
        """
        Test the Azure Storage connection
        
        Returns:
            dict: Connection status information
        """
        try:
            # Try to list containers to test connection
            containers = list(self.blob_service_client.list_containers(max_results=1))
            return {
                "status": "connected",
                "container_name": self.container_name,
                "account_name": self.blob_service_client.account_name,
                "container_exists": self.container_client.exists()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
