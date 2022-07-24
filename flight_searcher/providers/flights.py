import datetime
import json

import structlog
from aioredis import Redis

from ..api.schemas.flight import FlightResponse
from ..clients.http import HttpClient

FLIGHTS_URL = "https://api.skypicker.com/flights"
REDIS_FLIGHTS_KEY = "airports_flights:{src_airports}:{dst_airports}:{dep_date}"
CACHE_MINUTES = 30
PARTNER = "dominiktest"
MAX_DAYS_IN_PAST = 45


class FlightsProvider:
    def __init__(
        self,
        redis: Redis,
        http_client: HttpClient,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._redis = redis
        self._http_client = http_client
        self.log = logger.bind(name="flights")

    @staticmethod
    def _build_airport_params(airports: list[str]) -> str:
        items = [f"airport:{x}" for x in airports]
        return ",".join(items)

    def _get_flights_from_kiwi(
        self,
        src_airports: list[str],
        dst_airports: list[str],
        departure_date: datetime.date,
    ) -> list[FlightResponse]:
        _date = departure_date.strftime("%Y-%m-%d")
        params = {
            "partner": PARTNER,
            "fly_from": self._build_airport_params(src_airports),
            "fly_to": self._build_airport_params(dst_airports),
            "depart_after": f"{_date}T00:00",
            "depart_before": f"{_date}T23:59",
        }
        kiwi_flights = self._http_client.get(FLIGHTS_URL, params=params).json()  # type: ignore
        response_flights = []
        for flight in kiwi_flights["data"]:
            _item = FlightResponse(
                src=flight["flyFrom"], dst=flight["flyTo"], price=flight["price"]
            )
            response_flights.append(_item)
        return response_flights

    async def get_flights(
        self,
        src_airports: list[str],
        dst_airports: list[str],
        departure_date: datetime.date,
    ) -> list[FlightResponse]:
        # date validation
        days_to_fly = (departure_date - datetime.date.today()).days
        if days_to_fly < -MAX_DAYS_IN_PAST:
            raise DateTooOld(f"You can search max {MAX_DAYS_IN_PAST} days in past.")
        # search in cache
        _src = ",".join(src_airports)
        _dst = ",".join(dst_airports)
        _date = str(departure_date)
        _key = REDIS_FLIGHTS_KEY.format(
            src_airports=_src, dst_airports=_dst, dep_date=_date
        )
        self.log.info("get_flights.start", key=_key)
        flights = await self._redis.get(_key)
        if not flights:
            self.log.info("get_flights.get_from_kiwi", key=_key)
            flights = self._get_flights_from_kiwi(
                src_airports, dst_airports, departure_date
            )
            raw_flights = [x.dict() for x in flights]
            _value = json.dumps(raw_flights)
            await self._redis.setex(_key, CACHE_MINUTES * 60, _value)
        else:
            self.log.info("get_flights.got_from_redis", key=_key)
            flights = json.loads(flights)
            flights = [FlightResponse.construct(**x) for x in flights]
        return flights


class DateTooOld(Exception):
    pass
