"""Script to run the FastAPI application."""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Use 0.0.0.0 to allow connections from other devices on the network
    # This is important for mobile app development
    host = "0.0.0.0" if not settings.DEBUG else settings.API_HOST
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

