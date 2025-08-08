# YoobuMorph API

FastAPI application for processing and uploading images to Azure Blob Storage.

## 🚀 Features

- **Image Processing**: Square images with intelligent sizing
- **Azure Storage**: Upload processed images to Azure Blob Storage
- **Batch Processing**: Process multiple images with variations
- **RESTful API**: Clean FastAPI endpoints
- **Health Checks**: Monitor API and Azure connection status

## 📋 Requirements

- Python 3.8+
- Azure Storage Account
- FastAPI
- Pillow (PIL)
- Azure Storage Blob SDK

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/DavePHP32/projectYoobuMorph.git
cd projectYoobuMorph
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Azure Storage**
   
   **Local Development:**
   - Copy your Azure connection string to `config/yoobumorph_config.json`
   
   **Production:**
   - Set environment variable `AZURE_CONNECTION_STRING`
   - Set environment variable `AZURE_CONTAINER_NAME` (optional, defaults to "processed-images")

4. **Run the application**
```bash
uvicorn src.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Health Checks
- `GET /health` - Check API and Azure connection status
- `GET /health/ping` - Simple ping endpoint

### Image Processing
- `POST /images/process-batch` - Process multiple images with variations
- `GET /images/info` - Get image processing configuration

### Admin
- `DELETE /admin/container` - Delete Azure container
- `POST /admin/container` - Create Azure container
- `POST /admin/container/recreate` - Recreate Azure container
- `GET /admin/container/status` - Get container status
- `GET /admin/blobs` - List all blobs in container

## 📝 API Usage

### Process Images
```json
POST /images/process-batch
{
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "variations": [
        {
          "name": "product_main",
          "size": [750, 750]
        },
        {
          "name": "product_thumb",
          "size": [300, 300]
        }
      ]
    }
  ]
}
```

### Response
```json
{
  "azure_urls": [
    "https://storage.blob.core.windows.net/processed-images/product_main_product_thumb_ABC123_SLY_750.jpg"
  ]
}
```

## 🚀 Deployment

### Render (Recommended)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables:
   - `AZURE_CONNECTION_STRING`: Your Azure connection string
   - `AZURE_CONTAINER_NAME`: processed-images (optional)

### Railway
1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically

### Fly.io
1. Install Fly CLI
2. Run `fly launch`
3. Set secrets: `fly secrets set AZURE_CONNECTION_STRING="your-connection-string"`

### Heroku
1. Create Heroku app
2. Set config vars in Heroku dashboard
3. Deploy with `git push heroku main`

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_CONNECTION_STRING` | Azure Storage connection string | Yes |
| `AZURE_CONTAINER_NAME` | Azure container name | No (default: processed-images) |

## 📁 Project Structure

```
projectYoobuMorph/
├── src/
│   ├── fastapi_app.py      # Main FastAPI application
│   ├── image_processor.py  # Image processing logic
│   └── naming_convention.py # File naming logic
├── routes/
│   ├── health.py           # Health check endpoints
│   ├── images.py           # Image processing endpoints
│   └── admin.py            # Admin endpoints
├── utils/
│   └── azure_storage.py    # Azure Storage operations
├── config/
│   └── yoobumorph_config.json # Local configuration
├── Dockerfile              # Docker configuration
├── render.yaml             # Render deployment config
└── requirements.txt        # Python dependencies
```

## 🔒 Security

- Azure connection strings are stored as environment variables in production
- Local config file is gitignored to prevent secrets from being committed
- Azure Storage uses SAS tokens for secure access

## 📄 License

MIT License 