"""
Image processing routes for YoobuMorph FastAPI application
========================================================

This module contains endpoints for processing and uploading images to Azure Storage.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Union
import requests
from pathlib import Path
import tempfile
import os

from src.naming_convention import NamingConvention
from src.image_processor import ImageProcessor
from utils.azure_storage import AzureStorageManager

router = APIRouter(prefix="/images", tags=["images"])

# Global Azure Storage Manager
azure_storage_manager: AzureStorageManager = None

# Initialize processors
naming_convention = NamingConvention()
image_processor = ImageProcessor()

class ImageVariation(BaseModel):
    name: str
    size: tuple[int, int] | None = None  # None = détection automatique
    background_color: tuple[int, int, int] = (255, 255, 255)

class ImageRequest(BaseModel):
    url: str
    variations: List[ImageVariation] = []

class BatchRequest(BaseModel):
    images: List[ImageRequest]

class BatchResponse(BaseModel):
    azure_urls: List[str]

def set_azure_config(connection_string: str, container_name: str):
    """Set Azure configuration for image processing"""
    global azure_storage_manager
    azure_storage_manager = AzureStorageManager(connection_string, container_name)

def upload_to_azure_blob(local_path: Path, blob_name: str) -> str:
    """Upload a file to Azure Blob Storage"""
    if not azure_storage_manager:
        raise HTTPException(status_code=500, detail="Azure Storage not configured. Please set AZURE_CONNECTION_STRING environment variable.")
    
    return azure_storage_manager.upload_file(local_path, blob_name)

def process_and_upload_image_variations(url: str, variations: List[ImageVariation], all_variation_names: List[str]) -> List[dict]:
    """Download, process and upload image variations to Azure Storage"""
    # Download image temporarily
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Download error: {url}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_in:
        tmp_in.write(response.content)
        tmp_in.flush()
        tmp_in_path = Path(tmp_in.name)

    processed_variations = []
    
    try:
        # Detect original image size and determine target size
        from PIL import Image
        with Image.open(tmp_in_path) as img:
            original_width, original_height = img.size
            
            # Determine target size based on image orientation
            if original_width > original_height:
                # Horizontal image: use width as reference
                auto_size = original_width
            elif original_height > original_width:
                # Vertical image: use height as reference
                auto_size = original_height
            else:
                # Square image: keep original size
                auto_size = original_width  # or original_height, they're the same
        
        for variation in variations:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_out:
                tmp_out_path = Path(tmp_out.name)

            # Use provided size or auto-detect
            target_size = variation.size if variation.size is not None else (auto_size, auto_size)
            
            # Resize image according to variation settings
            image_processor.squareify_image(
                tmp_in_path, 
                tmp_out_path, 
                target_size, 
                variation.background_color
            )

            # Generate blob name using naming convention with all variation names
            unique_id = naming_convention._generate_unique_id()
            
            # Use the combined variation names passed as parameter
            combined_names = '_'.join(all_variation_names)
            product_name = naming_convention._normalize_product_name(combined_names)
            
            blob_name = f"{product_name}_{unique_id}_SLY_{target_size[0]}.jpg"
            
            # Upload to Azure (without SAS for public access)
            azure_url = upload_to_azure_blob(tmp_out_path, blob_name)
            
            processed_variations.append({
                "name": variation.name,
                "size": target_size,
                "background_color": variation.background_color,
                "azure_url": azure_url,
                "original_size": (original_width, original_height)
            })
            
            os.remove(tmp_out_path)
            
    finally:
        os.remove(tmp_in_path)
    
    return processed_variations

@router.post("/process-batch", response_model=BatchResponse)
def process_batch(data: BatchRequest):

    azure_urls = []
    
    for image_request in data.images:
        try:
            # Get all variation names for this image (or use default if none)
            if image_request.variations:
                all_variation_names = [var.name for var in image_request.variations]
            else:
                # Use default naming if no variations providedkaaa
                all_variation_names = ["image"]
            
            variations = process_and_upload_image_variations(
                image_request.url, 
                image_request.variations if image_request.variations else [ImageVariation(name="image")],
                all_variation_names
            )
            
            if variations:
                azure_urls.append(variations[0]['azure_url'])
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing {image_request.url}: {str(e)}"
            )
    
    return BatchResponse(azure_urls=azure_urls)

@router.post("/process-urls")
def process_urls_legacy(data: dict):
    """Legacy endpoint - converts old format to new format"""
    urls = data.get("urls", [])
    if isinstance(urls, str):
        urls = [urls]
    
    images = []
    for i, url in enumerate(urls):
        images.append(ImageRequest(
            url=url,
            variations=[ImageVariation(name=f"image_{i+1}")]
        ))
    
    batch_request = BatchRequest(images=images)
    return process_batch(batch_request)

@router.get("/info")
def get_image_info():
    """Get information about image processing configuration"""
    return {
        "target_size": [750, 750],
        "background_color": [255, 255, 255],
        "azure_container": AZURE_CONTAINER_NAME,
        "supported_formats": [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]
    }
