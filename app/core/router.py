import pkgutil
from importlib import import_module
from fastapi import APIRouter
from app.api import healthcheck
from app.core.config import settings
import app.api as root_api

router = APIRouter()

# Health check endpoint
router.include_router(healthcheck.router)

# Auto-load all versioned APIs (v1, v2, ...)
for finder, subpackage_name, is_pkg in pkgutil.iter_modules(root_api.__path__):
    if is_pkg and subpackage_name.startswith("v"):
        subpackage = import_module(f"{root_api.__name__}.{subpackage_name}")
        for _, module_name, _ in pkgutil.iter_modules(subpackage.__path__):
            api_module = import_module(f"{subpackage.__name__}.{module_name}")
            version_router = getattr(api_module, "router", None)
            if version_router:
                # Chỉ include 1 lần với prefix version
                router.include_router(
                    version_router,
                    prefix=f"/{subpackage_name}"
                )
