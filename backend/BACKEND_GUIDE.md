# Backend Development Guide

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Architecture Patterns](#architecture-patterns)
4. [Coding Conventions](#coding-conventions)
5. [Adding New Features](#adding-new-features)
6. [API Structure](#api-structure)
7. [Authentication & Authorization](#authentication--authorization)
8. [Database Models](#database-models)
9. [Schemas (Pydantic)](#schemas-pydantic)
10. [Controllers](#controllers)
11. [Routers](#routers)
12. [Common Utilities](#common-utilities)
13. [Settings & Configuration](#settings--configuration)
14. [Best Practices](#best-practices)

---

## Overview

This backend is built with:
- **Django 6.0+**: Web framework
- **Django Ninja**: Fast API framework for Django (similar to FastAPI)
- **Pydantic**: Data validation and settings management
- **PostgreSQL**: Database
- **Python 3.12+**: Programming language
- **Ruff**: Linter and formatter

### Key Features

- RESTful API with automatic OpenAPI documentation
- JWT-based authentication
- API key authentication for devices
- Modular app-based architecture
- Type hints throughout
- Pydantic schemas for request/response validation

---

## Project Structure

```
backend/
├── sentry/                          # Main Django project
│   ├── api/                         # API routing layer
│   │   ├── router.py               # Main API router (NinjaAPI instance)
│   │   └── v1/
│   │       └── router.py           # API v1 router (groups feature routers)
│   │
│   ├── core/                       # Core app (users, auth, loved ones)
│   │   ├── apps.py                 # App configuration
│   │   ├── auth/                   # Authentication logic
│   │   │   ├── jwt.py             # JWT token creation/validation
│   │   │   ├── api_key.py         # API key authentication
│   │   │   ├── backends.py        # Custom auth backends
│   │   │   └── utils.py            # Auth utilities
│   │   ├── controllers/           # Business logic (request handlers)
│   │   │   ├── auth_controller.py
│   │   │   ├── user_controller.py
│   │   │   └── loved_one_controller.py
│   │   ├── models/                 # Database models
│   │   │   ├── user.py
│   │   │   ├── loved_one.py
│   │   │   ├── tokens.py
│   │   │   └── managers/          # Custom model managers
│   │   ├── router/                 # API route definitions
│   │   │   ├── core_router.py    # Groups all core routers
│   │   │   ├── auth_router.py
│   │   │   ├── user_router.py
│   │   │   └── loved_one_router.py
│   │   ├── schemas/                # Pydantic schemas (request/response)
│   │   │   ├── auth_schema.py
│   │   │   ├── user_schema.py
│   │   │   └── loved_one_schema.py
│   │   ├── migrations/            # Database migrations
│   │   ├── templates/             # Email templates
│   │   ├── utils/                  # Utility functions
│   │   │   └── user_utils.py
│   │   └── management/            # Django management commands
│   │       └── commands/
│   │
│   ├── device/                     # Device app (IoT device management)
│   │   ├── apps.py
│   │   ├── controllers/
│   │   │   └── device_controller.py
│   │   ├── models/
│   │   │   └── sensor_data.py
│   │   ├── router/
│   │   │   └── device_router.py
│   │   └── schemas/
│   │       └── device_schema.py
│   │
│   ├── audit/                      # Audit logging app
│   │   ├── models/
│   │   │   └── audit_log.py
│   │   └── schemas/
│   │
│   ├── common/                     # Shared utilities and constants
│   │   ├── constants/
│   │   │   ├── choices/           # Django model choices
│   │   │   │   ├── audit/
│   │   │   │   ├── token/
│   │   │   │   └── misc/
│   │   │   └── messages/          # User-facing messages
│   │   │       ├── core/
│   │   │       └── general_messages.py
│   │   └── utils/
│   │       └── file_utils.py
│   │
│   ├── sentry/                     # Django project settings
│   │   ├── settings/
│   │   │   ├── base.py           # Base settings
│   │   │   ├── config.py         # Pydantic settings (env vars)
│   │   │   ├── dev.py            # Development settings
│   │   │   └── prod.py           # Production settings
│   │   ├── urls.py                # Main URL configuration
│   │   ├── wsgi.py                # WSGI application
│   │   └── asgi.py                # ASGI application
│   │
│   ├── manage.py                   # Django management script
│   ├── logs/                       # Application logs
│   └── media/                      # User-uploaded files
│
├── pyproject.toml                  # Project dependencies and config
├── poetry.lock                     # Locked dependencies
└── README.md
```

---

## Architecture Patterns

### 1. **Layered Architecture**

```
┌─────────────────────────────────────┐
│         API Layer (Routers)         │  ← Route definitions, auth decorators
├─────────────────────────────────────┤
│      Controller Layer (Business)     │  ← Business logic, request handling
├─────────────────────────────────────┤
│         Schema Layer (Pydantic)      │  ← Request/response validation
├─────────────────────────────────────┤
│         Model Layer (Django ORM)     │  ← Database models, queries
└─────────────────────────────────────┘
```

### 2. **App-Based Organization**

Each feature domain is a separate Django app:
- `core`: User management, authentication, loved ones
- `device`: IoT device management, sensor data
- `audit`: Audit logging
- `common`: Shared utilities

### 3. **Request Flow**

```
Client Request
    ↓
API Router (router.py)
    ↓
Authentication (JWT/API Key)
    ↓
Controller (business logic)
    ↓
Model (database operations)
    ↓
Schema (response serialization)
    ↓
Client Response
```

---

## Coding Conventions

### 1. **Type Hints**

Always use type hints for function parameters and return types:

```python
from typing import Any
from django.http import HttpRequest

def get_user_info(request: HttpRequest) -> dict[str, Any]:
    """Get current user information."""
    # ...
    return {"message": "Success", "user": user_data}
```

### 2. **Docstrings**

Use Google-style docstrings:

```python
def update_user_info(
    request: HttpRequest,
    data: UserUpdateRequest,
) -> dict[str, Any]:
    """Update user information.

    Args:
        request: The HTTP request object
        data: The user update data

    Returns:
        Dictionary containing the success/error message

    Raises:
        ValidationError: If email already exists
    """
```

### 3. **Import Organization**

1. Standard library imports
2. Third-party imports
3. Django imports
4. Local app imports

```python
import contextlib
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja import Schema

from core.schemas import UserSchema
```

### 4. **Naming Conventions**

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Models**: `PascalCase` (singular: `User`, not `Users`)
- **Routers**: `{feature}_router.py`
- **Controllers**: `{feature}_controller.py`
- **Schemas**: `{feature}_schema.py`

### 5. **Line Length**

Maximum line length: **120 characters** (configured in `pyproject.toml`)

---

## Adding New Features

### Step-by-Step Guide

#### 1. **Create a New App (if needed)**

```bash
cd backend/sentry
python manage.py startapp <app_name>
```

#### 2. **Define Database Models**

**File**: `{app}/models/{model_name}.py`

```python
"""User model."""

from django.db import models

class User(AbstractUser):
    """Custom user model."""

    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
        ]
```

#### 3. **Create Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 4. **Define Pydantic Schemas**

**File**: `{app}/schemas/{feature}_schema.py`

```python
"""User schema."""

from ninja import Schema

class UserSchema(Schema):
    """User schema."""

    id: int
    username: str
    email: str
    first_name: str

class UserUpdateRequest(Schema):
    """User update request schema."""

    first_name: str | None = None
    last_name: str | None = None
```

#### 5. **Create Controller (Business Logic)**

**File**: `{app}/controllers/{feature}_controller.py`

```python
"""User controller."""

from typing import Any
from django.http import HttpRequest
from core.schemas import UserSchema, UserUpdateRequest

def get_user_info(request: HttpRequest) -> dict[str, Any]:
    """Get current user information."""
    user = request.user
    user_schema = UserSchema.model_validate(user)
    return {
        "message": "User information fetched successfully",
        "user": user_schema.model_dump(),
    }
```

#### 6. **Create Router (API Endpoints)**

**File**: `{app}/router/{feature}_router.py`

```python
"""User router."""

from typing import Any
from django.http import HttpRequest
from ninja import Router
from core.auth.jwt import JwtAuth
from core.controllers.user_controller import get_user_info
from core.schemas import UserUpdateRequest

user_router = Router(tags=["user"])

@user_router.get("/me/info", auth=JwtAuth())
def user_info_endpoint(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get current user information endpoint."""
    return get_user_info(request)
```

#### 7. **Register Router in Feature Router**

**File**: `{app}/router/{app}_router.py`

```python
"""Core router."""

from ninja import Router
from .user_router import user_router

core_router = Router(tags=["core"])
core_router.add_router("user", user_router)
```

#### 8. **Register Feature Router in v1 Router**

**File**: `api/v1/router.py`

```python
"""API v1 router."""

from core.router import core_router
from ninja import Router

router_v1 = Router(tags=["v1"])
router_v1.add_router("core", core_router)
```

#### 9. **Add App to INSTALLED_APPS**

**File**: `sentry/settings/base.py`

```python
INSTALLED_APPS = [
    # ...
    "core",
    "device",
    # Add your app here
]
```

---

## API Structure

### URL Structure

```
/api/v1/{feature}/{resource}/{action}
```

**Examples:**
- `GET /api/v1/core/user/me/info` - Get current user info
- `PUT /api/v1/core/user/me/update` - Update current user
- `POST /api/v1/core/auth/login` - Login
- `POST /api/v1/device/data` - Receive device data

### Router Hierarchy

```
api (NinjaAPI)
  └── v1 (Router)
      ├── core (Router)
      │   ├── auth (Router)
      │   ├── user (Router)
      │   └── loved-one (Router)
      └── device (Router)
```

### Endpoint Definition Pattern

```python
@router.get("/endpoint", auth=JwtAuth(), response=ResponseSchema)
def endpoint_function(
    request: HttpRequest,
    query_param: str | None = None,
) -> ResponseSchema:
    """Endpoint description."""
    # Call controller
    result = controller_function(request, query_param)
    return result
```

---

## Authentication & Authorization

### JWT Authentication (User Endpoints)

**Usage:**
```python
from core.auth.jwt import JwtAuth, VerifiedJwtAuth

@router.get("/endpoint", auth=JwtAuth())
def protected_endpoint(request: HttpRequest):
    user = request.user  # Available after authentication
    # ...
```

**Types:**
- `JwtAuth()`: Requires valid JWT token
- `VerifiedJwtAuth()`: Requires valid JWT + verified email

### API Key Authentication (Device Endpoints)

**Usage:**
```python
from core.auth.api_key import DeviceAPIKeyAuth

device_router = Router(tags=["device"], auth=DeviceAPIKeyAuth())

@device_router.post("/data")
def device_endpoint(request: HttpRequest):
    # Device authenticated via API key
    # ...
```

### Creating Tokens

```python
from core.auth.jwt import create_token_pair, create_access_token
from datetime import timedelta

# Create token pair (access + refresh)
tokens = create_token_pair(user_schema)

# Create custom token
access_token = create_access_token(
    data={"sub": str(user.id), "username": user.username},
    expires_in_mins=timedelta(minutes=60),
)
```

---

## Database Models

### Model Structure

```python
"""User model."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers.user_manager import UserManager

class User(AbstractUser):
    """Custom user model."""

    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=255)
    
    objects = UserManager()  # Custom manager
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
        ]
```

### Best Practices

1. **Use `blank=True` instead of `null=True` for CharField/TextField**
   ```python
   middle_name = models.CharField(max_length=255, blank=True)  # ✅
   # Not: null=True  # ❌
   ```

2. **Always add indexes for frequently queried fields**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=["email"]),
           models.Index(fields=["created_at"]),
       ]
   ```

3. **Use custom managers for complex queries**
   ```python
   # models/managers/user_manager.py
   class UserManager(models.Manager):
       def active_users(self):
           return self.filter(is_active=True)
   ```

4. **Use `ordering` in Meta for default ordering**
   ```python
   class Meta:
       ordering = ["-created_at"]  # Newest first
   ```

---

## Schemas (Pydantic)

### Request Schemas

```python
"""User schema."""

from ninja import Schema
from pydantic import field_validator

class UserUpdateRequest(Schema):
    """User update request schema."""

    first_name: str | None = None
    last_name: str | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def reject_none_or_empty(cls, v: str | None) -> str | None:
        """Reject None or empty string values."""
        if v is None:
            raise ValueError("This field cannot be None.")
        if isinstance(v, str) and v.strip() == "":
            raise ValueError("This field cannot be empty.")
        return v
```

### Response Schemas

```python
class UserSchema(Schema):
    """User schema."""

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
```

### Converting Models to Schemas

```python
from core.schemas import UserSchema

# In controller
user = User.objects.get(id=user_id)
user_schema = UserSchema.model_validate(user)
return {"user": user_schema.model_dump()}
```

---

## Controllers

### Controller Pattern

Controllers contain **business logic** and handle requests:

```python
"""User controller."""

from typing import Any
from django.http import HttpRequest
from django.db import transaction
from core.schemas import UserSchema, UserUpdateRequest

def get_user_info(request: HttpRequest) -> dict[str, Any]:
    """Get current user information.

    Args:
        request: The HTTP request object

    Returns:
        Dictionary containing the current user information
    """
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    user_schema = UserSchema.model_validate(user)
    return {
        "message": "User information fetched successfully",
        "user": user_schema.model_dump(),
    }

def update_user_info(
    request: HttpRequest,
    data: UserUpdateRequest,
) -> dict[str, Any]:
    """Update user information."""
    user_id = request.user.id
    
    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    if update_data:
        User.objects.filter(id=user_id).update(**update_data)
    
    return {"message": "User information updated successfully"}
```

### Best Practices

1. **Keep controllers thin** - Move complex logic to utils/{model_name}_utils.py
2. **Use transactions for multi-step operations**
   ```python
   from django.db import transaction
   
   with transaction.atomic():
       # Multiple database operations
       user.save()
       related_model.save()
   ```

3. **Return consistent response format**
   ```python
   return {
       "message": "Success message",
       "data": {...},  # Optional
   }
   ```

4. **Handle errors appropriately**
   ```python
   from ninja.errors import HttpError
   
   if not user:
       raise HttpError(status_code=404, message="User not found")
   ```

---

## Routers

### Router Structure

```python
"""User router."""

from typing import Any
from django.http import HttpRequest
from ninja import Router
from core.auth.jwt import JwtAuth
from core.controllers.user_controller import get_user_info
from core.schemas import UserSchema, UserUpdateRequest

# Create router with tag
user_router = Router(tags=["user"])

# Define endpoints
@user_router.get("/me/info", auth=JwtAuth(), response=dict[str, Any])
def user_info_endpoint(request: HttpRequest) -> dict[str, Any]:
    """Get current user information endpoint."""
    return get_user_info(request)

@user_router.put("/me/update", auth=JwtAuth())
def update_user_endpoint(
    request: HttpRequest,
    data: UserUpdateRequest,
) -> dict[str, Any]:
    """Update current user's information endpoint."""
    return update_user_info(request, data)
```

### Router Registration

**Feature Router** (`core/router/core_router.py`):
```python
from .user_router import user_router

core_router = Router(tags=["core"])
core_router.add_router("user", user_router)
```

**v1 Router** (`api/v1/router.py`):
```python
from core.router import core_router

router_v1 = Router(tags=["v1"])
router_v1.add_router("core", core_router)
```

**Main API** (`api/router.py`):
```python
from .v1.router import router_v1

api = NinjaAPI(title="Sentry API", version="1.0.0")
api.add_router("/v1", router_v1)
```

### HTTP Methods

- `@router.get()` - GET request
- `@router.post()` - POST request
- `@router.put()` - PUT request
- `@router.patch()` - PATCH request
- `@router.delete()` - DELETE request

---

## Common Utilities

### Constants & Messages

**File**: `common/constants/messages/core/auth_messages.py`

```python
"""Authentication messages."""

from typing import Final

class AuthMessages:
    """Authentication messages."""

    class Login:
        """Login messages."""
        SUCCESS: Final[str] = "Login successful."
        WRONG_CREDS: Final[str] = "Incorrect credentials."
```

**Usage:**
```python
from common.constants.messages.core.auth_messages import AuthMessages

return {"message": AuthMessages.Login.SUCCESS}
```

### File Utilities

**File**: `common/utils/file_utils.py`

```python
"""File utilities."""

def validate_image_file(file):
    """Validate image file."""
    # ...
```

---

## Utilities

### Model-Specific Utilities

Each model should have its own utility file for complex business logic related to that model:

**File**: `{app}/utils/{model_name}_utils.py`

```python
"""User utilities."""

from typing import Any
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_user_email(email: str) -> bool:
    """Validate user email format and uniqueness.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid and available, False otherwise
    """
    # Complex validation logic
    if User.objects.filter(email=email).exists():
        return False
    return True

def format_user_name(user: User) -> str:
    """Format user's full name.
    
    Args:
        user: User instance
        
    Returns:
        Formatted full name string
    """
    parts = [user.first_name]
    if user.middle_name:
        parts.append(user.middle_name)
    parts.append(user.last_name)
    return " ".join(parts)
```

**Usage in Controller:**
```python
from core.utils.user_utils import format_user_name

def get_user_info(request: HttpRequest) -> dict[str, Any]:
    """Get current user information."""
    user = request.user
    full_name = format_user_name(user)  # Use utility function
    # ...
```

### Best Practices

1. **One utility file per model** - `utils/{model_name}_utils.py` (e.g., `user_utils.py`, `device_utils.py`)
2. **Keep utilities focused** - Each function should have a single responsibility
3. **Use utilities for complex logic** - Keep controllers thin by moving complex operations to utilities
4. **Document utilities** - Add clear docstrings explaining what each utility does

---

## Settings & Configuration

### Settings Structure

**Pydantic Settings** (`sentry/settings/config.py`):
```python
"""Pydantic settings for the application."""

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""

    django_secret_key: str = Field(default="...")
    django_debug: bool = Field(default=True)
    database_url: str | None = Field(default=None)
    jwt_secret_key: str = Field(default="...")
    
    class Config:
        env_file = ".env"

settings: Settings = Settings()
```

**Django Settings** (`sentry/settings/base.py`):
```python
"""Django settings for sentry project."""

from .config import settings

SECRET_KEY = settings.django_secret_key
DEBUG = settings.django_debug
```

---

## Best Practices

### 1. **Error Handling**

```python
from ninja.errors import HttpError

def get_user(user_id: int):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(status_code=404, message="User not found")
```

### 2. **Database Queries**

- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many/reverse foreign keys
- Use `only()` or `defer()` to limit fields
- Use `values()` or `values_list()` for simple queries

```python
# ✅ Good
users = User.objects.select_related('profile').all()

# ❌ Bad
users = User.objects.all()
for user in users:
    profile = user.profile  # N+1 query problem
```

### 3. **Transaction Management**

```python
from django.db import transaction

@transaction.atomic
def transfer_money(from_account, to_account, amount):
    from_account.balance -= amount
    from_account.save()
    to_account.balance += amount
    to_account.save()
```

### 4. **Logging**

```python
import logging

logger = logging.getLogger(app_name)
*Refer to logging settings in sentry/settings*

def process_data(data):
    logger.info("Processing data: %s", data)
    try:
        # Process
        logger.debug("Data processed successfully")
    except Exception as e:
        logger.error("Error processing data: %s", e, exc_info=True)
        raise
```

### 5. **Code Organization**

- **One file per model** (unless closely related)
- **One controller function per endpoint**
- **Group related schemas in one file**
- **Keep routers thin** - delegate to controllers

### 6. **Security**

- Always validate input via Pydantic schemas
- Use parameterized queries (Django ORM does this automatically)
- Never expose sensitive data in responses
- Use HTTPS in production
- Validate file uploads (type, size)

### 7. **Performance**

- Add database indexes for frequently queried fields
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Cache expensive operations when appropriate
- Use `bulk_create()` and `bulk_update()` for multiple records

### 8. **Documentation**

- Write clear docstrings for all functions
- Document complex business logic
- Keep API endpoint descriptions clear
- Update this guide when patterns change

---

## Common Patterns

### Pattern 1: CRUD Operations

```python
# Controller
def create_item(request: HttpRequest, data: ItemCreateRequest) -> dict:
    item = Item.objects.create(**data.model_dump())
    return {"message": "Item created", "item": ItemSchema.model_validate(item)}

def get_item(request: HttpRequest, item_id: int) -> dict:
    item = Item.objects.get(id=item_id)
    return {"item": ItemSchema.model_validate(item)}

def update_item(request: HttpRequest, item_id: int, data: ItemUpdateRequest) -> dict:
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    Item.objects.filter(id=item_id).update(**update_data)
    return {"message": "Item updated"}

def delete_item(request: HttpRequest, item_id: int) -> dict:
    Item.objects.filter(id=item_id).delete()
    return {"message": "Item deleted"}

# Router
@router.post("/items", auth=JwtAuth())
def create_item_endpoint(request: HttpRequest, data: ItemCreateRequest):
    return create_item(request, data)

@router.get("/items/{item_id}", auth=JwtAuth())
def get_item_endpoint(request: HttpRequest, item_id: int):
    return get_item(request, item_id)
```

### Pattern 2: Pagination

```python
from ninja import Schema

class PaginatedResponse(Schema):
    """Paginated response schema."""
    items: list[ItemSchema]
    total: int
    page: int
    page_size: int

def get_items(request: HttpRequest, page: int = 1, page_size: int = 10):
    items = Item.objects.all()
    total = items.count()
    items = items[(page - 1) * page_size : page * page_size]
    return {
        "items": [ItemSchema.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
```

### Pattern 3: File Upload

```python
from ninja import File
from ninja.files import UploadedFile

@router.put("/profile-picture", auth=JwtAuth())
def update_profile_picture(
    request: HttpRequest,
    profile_picture: File[UploadedFile],
):
    # Validate file
    if not profile_picture.content_type.startswith("image/"):
        raise HttpError(400, "File must be an image")
    
    # Save file
    user = request.user
    user.profile_picture = profile_picture
    user.save()
    
    return {"message": "Profile picture updated"}
```

---

## Quick Reference

### Creating a New Endpoint

1. Add schema in `{app}/schemas/{feature}_schema.py`
2. Add controller function in `{app}/controllers/{feature}_controller.py`
3. Add route in `{app}/router/{feature}_router.py`
4. Register router in feature router
5. Test endpoint

### Common Commands

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run linter
ruff check .

# Format code
ruff format .
```

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Ninja Documentation](https://django-ninja.rest-framework.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

## Questions or Issues?

If you have questions about the backend structure or need help implementing a feature, refer to this guide or check existing code for examples.

**Last Updated**: 2025

