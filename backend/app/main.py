"""Backend ASGI application and CLI entry point."""

from .api.server import create_app, run

app = create_app()
__all__ = ["app", "create_app", "run"]

if __name__ == "__main__":
    run()
