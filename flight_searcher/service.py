"""Services module."""
import datetime

import structlog

from .api.schemas.flight import FlightResponse
from .providers.airports import AirportsProvider
from .providers.flights import FlightsProvider


class Service:
    def __init__(
        self,
        airports_provider: AirportsProvider,
        flights_provider: FlightsProvider,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._airports_provider = airports_provider
        self._flights_provider = flights_provider
        self.log = logger.bind(logger_name="service")

    async def get_top_flights(
        self,
        src_country: str,
        dst_country: str,
        departure_date: datetime.date,
        top_count: int,
    ) -> list[FlightResponse]:
        self.log.info(
            "get_top_flights.start",
            src_country=src_country,
            dst_country=dst_country,
            departure_date=departure_date,
            top_count=top_count,
        )
        src_airports = await self._airports_provider.get_top_airports_by_country(
            src_country, top_count
        )
        dst_airports = await self._airports_provider.get_top_airports_by_country(
            dst_country, top_count
        )
        self.log.info(
            "get_top_flights.airports",
            src_country=src_country,
            dst_country=dst_country,
            src_airports=str(src_airports),
            dst_airports=str(dst_airports),
        )
        return await self._flights_provider.get_flights(
            src_airports, dst_airports, departure_date
        )
