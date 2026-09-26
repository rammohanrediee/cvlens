"""Backend ASGI application and CLI entry point."""

from .api.server import create_app, run

__all__ = ["create_app", "run"]

if __name__ == "__main__":
    run()
