"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.api import scanner, inventory, cart, users, bills

# Initialize database and tables
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    logger.warning("Application will continue but database operations may fail")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scanner.router)
app.include_router(inventory.router)
app.include_router(cart.router)
app.include_router(users.router)
app.include_router(bills.router)

# Legacy endpoints for backward compatibility
@app.get("/scan_barcode")
async def scan_barcode_legacy():
    """Legacy endpoint - calls new endpoint."""
    from app.api.scanner import scan_barcode
    return await scan_barcode()

@app.post("/add_product_inventory")
async def add_product_inventory_legacy():
    """Legacy endpoint - use /inventory/products instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use POST /inventory/products instead."
    )

@app.put("/modify_product_inventory/{barcode}")
async def modify_product_inventory_legacy():
    """Legacy endpoint - use PUT /inventory/products/{barcode} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use PUT /inventory/products/{barcode} instead."
    )

@app.delete("/delete_product_inventory/{barcode}")
async def delete_product_inventory_legacy():
    """Legacy endpoint - use DELETE /inventory/products/{barcode} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use DELETE /inventory/products/{barcode} instead."
    )

@app.put("/get_list_inventory")
async def get_list_inventory_legacy():
    """Legacy endpoint - use GET /inventory/products instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use GET /inventory/products instead."
    )

@app.post("/add_product_cart")
async def add_product_cart_legacy():
    """Legacy endpoint - use POST /cart/products instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use POST /cart/products instead."
    )

@app.put("/modify_product_cart/{barcode}")
async def modify_product_cart_legacy():
    """Legacy endpoint - use PUT /cart/products/{barcode} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use PUT /cart/products/{barcode} instead."
    )

@app.delete("/delete_product_cart/{barcode}")
async def delete_product_cart_legacy():
    """Legacy endpoint - use DELETE /cart/products/{barcode} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use DELETE /cart/products/{barcode} instead."
    )

@app.get("/get_list_cart")
async def get_list_cart_legacy():
    """Legacy endpoint - use GET /cart/products instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use GET /cart/products instead."
    )

@app.delete("/clear_cart")
async def clear_cart_legacy():
    """Legacy endpoint - use DELETE /cart/clear instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use DELETE /cart/clear instead."
    )

@app.post("/add_user")
async def add_user_legacy():
    """Legacy endpoint - use POST /users instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use POST /users instead."
    )

@app.put("/modify_user/{user_id}")
async def modify_user_legacy():
    """Legacy endpoint - use PUT /users/{user_id} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use PUT /users/{user_id} instead."
    )

@app.delete("/delete_user/{user_id}")
async def delete_user_legacy():
    """Legacy endpoint - use DELETE /users/{user_id} instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use DELETE /users/{user_id} instead."
    )

@app.get("/get_users")
async def get_users_legacy():
    """Legacy endpoint - use GET /users instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use GET /users instead."
    )

@app.get("/generate-bill")
async def generate_bill_legacy():
    """Legacy endpoint - use GET /bills/generate instead."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use GET /bills/generate instead."
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

