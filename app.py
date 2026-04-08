"""Root app module that re-exports the FastAPI app for convenience."""

from .server.app import app

__all__ = ["app"]
