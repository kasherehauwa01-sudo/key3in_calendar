from .auth import router as auth_router
from .notes import router as notes_router
from .notifications import router as notifications_router
from .system import router as system_router
from .recurring_events import router as recurring_events_router
__all__ = ["auth_router", "notes_router", "notifications_router", "system_router", "recurring_events_router"]
