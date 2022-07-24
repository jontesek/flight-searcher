"""Containers module."""

import structlog
from dependency_injector import containers, providers

from .clients import http, redis
from .providers.airports import AirportsProvider
from .providers.flights import FlightsProvider
from .service import Service


class Container(containers.DeclarativeContainer):

    # wiring_config = containers.WiringConfiguration(packages=["flight_searcher.api"])

    config = providers.Configuration(strict=True)

    # general
    logger = providers.Resource(
        structlog.get_logger,
    )

    redis_pool = providers.Resource(
        redis.init_redis_pool,
        url=config.redis_url,
    )

    http_client = providers.Resource(
        http.HttpClient,
        user_agent=config.user_agent,
        logger=logger,
    )

    # components
    flights_provider = providers.Factory(
        FlightsProvider,
        redis=redis_pool,
        http_client=http_client,
        logger=logger,
    )

    airports_provider = providers.Factory(
        AirportsProvider,
        redis=redis_pool,
        http_client=http_client,
        logger=logger,
    )

    # main app
    service = providers.Factory(
        Service,
        airports_provider=airports_provider,
        flights_provider=flights_provider,
        logger=logger,
    )
