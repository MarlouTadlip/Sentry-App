"""API v1 router."""

from core.router import core_router
from device.router import device_router
from ninja import Router

# Create a router for v1 endpoints
router_v1 = Router(tags=["v1"])

# Feature routers
router_v1.add_router("core", core_router)
router_v1.add_router("device", device_router)
