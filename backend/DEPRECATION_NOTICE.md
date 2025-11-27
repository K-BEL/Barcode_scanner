# Legacy Endpoints Deprecation Notice

## Overview

This document outlines the deprecation timeline for legacy API endpoints. All legacy endpoints will be removed in version 2.0.0 of the API.

## Migration Guide

### Current Status (v1.0.0)

Both legacy and versioned endpoints are available:
- **Legacy endpoints**: Available without `/api/v1/` prefix (e.g., `/inventory/products`)
- **Versioned endpoints**: Available with `/api/v1/` prefix (e.g., `/api/v1/inventory/products`)

### Deprecation Timeline

- **v1.0.0 - v1.9.x**: Legacy endpoints remain available but are marked as deprecated
- **v2.0.0**: Legacy endpoints will be completely removed

### Endpoint Mapping

#### Scanner Endpoints
- Legacy: `GET /scan/barcode`
- New: `GET /api/v1/scan/barcode`

#### Inventory Endpoints
- Legacy: `GET /inventory/products`, `POST /inventory/products`, etc.
- New: `GET /api/v1/inventory/products`, `POST /api/v1/inventory/products`, etc.

#### Cart Endpoints
- Legacy: `GET /cart/products`, `POST /cart/products`, etc.
- New: `GET /api/v1/cart/products`, `POST /api/v1/cart/products`, etc.

#### User Endpoints
- Legacy: `GET /users`, `POST /users`, etc.
- New: `GET /api/v1/users`, `POST /api/v1/users`, etc.

#### Bill Endpoints
- Legacy: `GET /bills/generate`
- New: `GET /api/v1/bills/generate`

### Additional Legacy Endpoints (to be removed)

The following endpoints in `main.py` are deprecated and will be removed:
- `GET /scan_barcode`
- `POST /add_product_inventory`
- `PUT /modify_product_inventory/{barcode}`
- `DELETE /delete_product_inventory/{barcode}`
- `PUT /get_list_inventory`
- `POST /add_product_cart`
- `PUT /modify_product_cart/{barcode}`
- `DELETE /delete_product_cart/{barcode}`
- `GET /get_list_cart`
- `DELETE /clear_cart`
- `POST /add_user`
- `PUT /modify_user/{user_id}`
- `DELETE /delete_user/{user_id}`
- `GET /get_users`
- `GET /generate-bill`

### Action Required

**Before v2.0.0 release:**
1. Update all API clients to use `/api/v1/` prefixed endpoints
2. Test all functionality with versioned endpoints
3. Remove any references to legacy endpoints from your codebase

### Support

If you have questions or need assistance with migration, please refer to the API documentation at `/docs` or contact the development team.

