import asyncio
import datetime

from dependency_injector.wiring import Provide, inject

from .container import Container
from .service import Service
from .settings import SETTINGS


@inject
async def main(service: Service = Provide[Container.service]):
    src_country = "DE"
    dst_country = "US"
    dep_date = datetime.date(2022, 10, 20)
    flights = await service.get_top_flights(src_country, dst_country, dep_date, 5)
    print(flights[:5])


if __name__ == "__main__":
    container = Container()
    # container.config.redis_url.from_value("redis://127.0.0.1/0")
    # container.config.user_agent.from_value("flight_searcher/master (jonas dev)")
    container.config.from_pydantic(SETTINGS)
    container.wire(modules=[__name__])

    asyncio.run(main())
