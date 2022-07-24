from collections import defaultdict

import pycountry
import structlog
from aioredis import Redis

from ..clients.http import HttpClient

LOCATIONS_URL = "https://api.skypicker.com/locations/dump?active_only=false&location_types=airport&limit=10000"
REDIS_AIRPORTS_KEY = "country_airports:{country}"
CACHE_HOURS = 24


class AirportsProvider:
    def __init__(
        self,
        redis: Redis,
        http_client: HttpClient,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._redis = redis
        self._http_client = http_client
        self.log = logger.bind(logger_name="airports")

    def _create_country_dict(self, locations: list[dict]) -> dict[str, list[dict]]:
        countries = defaultdict(list)
        for location in locations:
            country = location["city"]["country"]["code"]
            airport = {
                "code": location["code"],
                "popularity": location["dst_popularity_score"],
            }
            countries[country].append(airport)
        return countries

    def _sort_country_dict(self, countries: dict) -> dict:
        for country_code, airports in countries.items():
            _items = sorted(airports, key=lambda x: x["popularity"], reverse=True)
            countries[country_code] = _items
        return countries

    async def _get_new_country_dict_and_cache_to_redis(self) -> dict:
        airports = self._http_client.get(LOCATIONS_URL).json()  # type: ignore
        country_dict = self._create_country_dict(airports["locations"])
        country_dict = self._sort_country_dict(country_dict)
        for country_code, airports in country_dict.items():
            _airports = [x["code"] for x in airports]
            _key = REDIS_AIRPORTS_KEY.format(country=country_code)
            await self._redis.rpush(_key, *_airports)
            await self._redis.expire(_key, CACHE_HOURS * 3600)
        return country_dict

    async def get_top_airports_by_country(
        self, country: str, top_count: int = -1
    ) -> list[str]:
        if not pycountry.countries.get(alpha_2=country):
            raise InvalidCountry(country)
        _key = REDIS_AIRPORTS_KEY.format(country=country)
        self.log = self.log.bind(country=country, top_count=top_count)
        self.log.info("get_top_airports_by_country.start")
        airports = await self._redis.lrange(_key, 0, top_count)
        if not airports:
            self.log.info("get_top_airports_by_country.from_kiwi")
            country_dict = await self._get_new_country_dict_and_cache_to_redis()
            if country not in country_dict:
                raise AirportsForCountryNotFound(country)
            airports = [x["code"] for x in country_dict[country]]
        else:
            self.log.info("get_top_airports_by_country.got_from_redis")
        return airports[0:top_count]


class AirportsForCountryNotFound(Exception):
    pass


class InvalidCountry(Exception):
    pass
