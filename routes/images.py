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

class ProductImage(BaseModel):
    url: str
    variation_name: str

class ProductRequest(BaseModel):
    product_name: str
    images_list: List[ProductImage]

class BatchRequest(BaseModel):
    products: List[ProductRequest]

class ImageResult(BaseModel):
    url: str
    variation_name: str

class BatchResponse(BaseModel):
    processed_images: List[ImageResult]

def set_azure_config(connection_string: str, container_name: str):
    """Set Azure configuration for image processing"""
    global azure_storage_manager
    azure_storage_manager = AzureStorageManager(connection_string, container_name)

def upload_to_azure_blob(local_path: Path, blob_name: str) -> str:
    """Upload a file to Azure Blob Storage"""
    if not azure_storage_manager:
        raise HTTPException(status_code=500, detail="Azure Storage not configured. Please set AZURE_CONNECTION_STRING environment variable.")
    
    return azure_storage_manager.upload_file(local_path, blob_name)

def process_and_upload_image_variations(product_images: List[ProductImage], product_name: str) -> List[dict]:
    """Download, process and upload image variations to Azure Storage"""
    processed_variations = []
    
    for product_image in product_images:
        # Download image temporarily
        response = requests.get(product_image.url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Download error: {product_image.url}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_in:
            tmp_in.write(response.content)
            tmp_in.flush()
            tmp_in_path = Path(tmp_in.name)

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

            # Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_out:
                tmp_out_path = Path(tmp_out.name)

            # Determine target size based on image orientation and dimensions
            if original_width > original_height:
                # Image Horizontale: utiliser la largeur comme référence
                target_size = (original_width, original_width)
            elif original_height > original_width:
                # Image Verticale: utiliser la hauteur comme référence
                target_size = (original_height, original_height)
            else:
                # Image Carrée: ne pas modifier, garder la taille originale
                target_size = (original_width, original_height)
            
            # Resize image according to variation settings
            image_processor.squareify_image(
                tmp_in_path, 
                tmp_out_path, 
                target_size, 
                (255, 255, 255)  # Default white background
            )

            # Generate blob name using naming convention: product_name + variation_name + unique_id + SLY + size
            unique_id = naming_convention._generate_unique_id()
            
            # Normalize product name and variation name
            normalized_product_name = naming_convention._normalize_product_name(product_name)
            normalized_variation_name = naming_convention._normalize_product_name(product_image.variation_name)
            
            blob_name = f"{normalized_product_name}_{normalized_variation_name}_{unique_id}_SLY_{target_size[0]}.jpg"
            
            # Upload to Azure (without SAS for public access)
            azure_url = upload_to_azure_blob(tmp_out_path, blob_name)
            
            processed_variations.append({
                "variation_name": product_image.variation_name,
                "size": target_size,
                "background_color": (255, 255, 255),
                "azure_url": azure_url,
                "original_size": (original_width, original_height)
            })
            
            os.remove(tmp_out_path)
                
        finally:
            os.remove(tmp_in_path)
    
    return processed_variations

@router.post("/process-batch", response_model=BatchResponse)
def process_batch(data: BatchRequest):
    """
    Process and upload product images to Azure Storage.
    
    Expected request format:
    {
      "products": [
        {
          "product_name": "nom_du_produit",
          "images_list": [
            {
              "url": "https://example.com/image1.jpg",
              "variation_name": "main"
            },
            {
              "url": "https://example.com/image2.jpg", 
              "variation_name": "detail"
            }
          ]
        }
      ]
    }
    """
    results = []
    
    for product_request in data.products:
        try:
            variations = process_and_upload_image_variations(
                product_request.images_list,
                product_request.product_name
            )
            
            # Add all processed results to the response
            for variation in variations:
                results.append(ImageResult(
                    url=variation['azure_url'],
                    variation_name=variation['variation_name']
                ))
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing product {product_request.product_name}: {str(e)}"
            )
    
    return BatchResponse(processed_images=results)

@router.post("/process-urls")
def process_urls_legacy(data: dict):
    """Legacy endpoint - converts old format to new format"""
    urls = data.get("urls", [])
    if isinstance(urls, str):
        urls = [urls]
    
    images = []
    for i, url in enumerate(urls):
        images.append(ProductImage(
            url=url,
            variation_name=f"image_{i+1}"
        ))
    
    product_request = ProductRequest(
        product_name="legacy_product",
        images_list=images
    )
    batch_response = process_batch(BatchRequest(products=[product_request]))
    
    # Convert to legacy format for backward compatibility
    return {
        "azure_urls": [result.url for result in batch_response.processed_images]
    }

@router.get("/info")
def get_image_info():
    """Get information about image processing configuration"""
    return {
        "target_size": [750, 750],
        "background_color": [255, 255, 255],
        "azure_container": AZURE_CONTAINER_NAME,
        "supported_formats": [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]
    }
