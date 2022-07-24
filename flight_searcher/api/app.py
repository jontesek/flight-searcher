import logging

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration

from ..container import Container
from ..settings import SETTINGS
from .routers.health import router as health_router
from .routers.top_flights import router as top_flights_router


def create_app():
    # setup  DI
    container = Container()
    container.config.from_pydantic(SETTINGS)
    container.wire(packages=["flight_searcher.api"])

    app = FastAPI(
        title="Flight searcher",
        description="Searching for flights between countries",
        version="0.1.0",
        debug=SETTINGS.is_debug,
    )

    if not SETTINGS.is_local:
        # Send only critical log events to Sentry.
        sentry_logging = LoggingIntegration(
            level=logging.INFO, event_level=logging.CRITICAL
        )
        sentry_sdk.init(
            dsn=SETTINGS.sentry_dsn,
            environment=SETTINGS.environment,
            integrations=[sentry_logging],
        )
        app.add_middleware(SentryAsgiMiddleware)

    app.include_router(health_router)
    app.include_router(top_flights_router)

    return app
