from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager

# FastAPI: The root application object that wraps routes, middleware, and documentation.

# APIRouter: Splits routes across modular files (e.g., routers/auth.py, routers/users.py) and prefixes/tags them cleanly.

# asynccontextmanager: Used with FastAPI(lifespan=...) to manage startup/shutdown tasks (like connecting to databases or caching layers).


from fastapi import (
    Path,      # Route path params: /users/{user_id}
    Query,     # URL query strings: /items?page=1&limit=20
    Body,      # Raw or custom request body payloads
    Header,    # HTTP headers: Authorization, User-Agent
    Cookie,    # Client-side cookies
    Form,      # multipart/form-data for form fields
    File,      # Uploaded file raw bytes
    UploadFile # File stream with metadata (better for large uploads)
)

from typing import Annotated  # Standard modern pattern for declaring parameter metadata4

from pydantic import (
    BaseModel,    # Base schema class for request/response contracts
    Field,        # Validation rules: gt=0, min_length=3, description="..."
    EmailStr,     # Validates email formatting
    HttpUrl,      # Validates URLs
    ConfigDict,   # Model configuration (e.g., from_attributes=True for ORMs)
)


# Dependency Injection
# FastAPI's dependency injection system handles database sessions, authentication, permissions, and shared services:

from fastapi import Depends, Security
from fastapi.security import (
    OAuth2PasswordBearer,       # JWT/token extraction from Bearer headers
    OAuth2PasswordRequestForm,   # Standard form data for login endpoints
    APIKeyHeader,                # Header-based API key authentication
    HTTPBearer                   # Generic bearer scheme
)


from fastapi import (
    status,           # HTTP constant aliases (e.g., status.HTTP_201_CREATED)
    HTTPException,    # Raise client errors (e.g., 400 Bad Request, 404 Not Found)
    Response,         # Manual response control (set cookies, custom headers)
    Request           # Raw HTTP request object (client IP, raw body)
)
from fastapi.responses import (
    JSONResponse,     # Custom JSON output or error overrides
    StreamingResponse,# Large datasets, file downloads, or event streams
    FileResponse,     # Direct disk-to-client file sending
    RedirectResponse  # HTTP 301/302/307 redirects
)


from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware