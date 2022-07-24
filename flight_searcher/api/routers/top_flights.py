import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query

from ...container import Container
from ...providers.airports import AirportsForCountryNotFound, InvalidCountry
from ...providers.flights import DateTooOld
from ...service import Service
from ..schemas.flight import FlightResponse

router = APIRouter()


@router.get(
    "/top_flights/",
    response_model=list[FlightResponse],
    summary="Get flights between the most popular airports in the source and destination countries.",
)
@inject
async def top_flights(
    src_country: str = Query(None, description="alpha-2 country code"),
    dst_country: str = Query(None, description="alpha-2 country code"),
    departure_date: datetime.date = Query(
        None, description="YYYY-MM-DD format (departure airport timezone)"
    ),
    top_count: int = Query(
        3, description="How many airports to select for each country.", ge=1, le=5
    ),
    service: Service = Depends(Provide[Container.service]),
):
    try:
        return await service.get_top_flights(
            src_country, dst_country, departure_date, top_count
        )
    except (DateTooOld, AirportsForCountryNotFound, InvalidCountry) as e:
        _msg = f"{type(e).__name__}: {str(e)}"
        raise HTTPException(status_code=422, detail=_msg) from e
