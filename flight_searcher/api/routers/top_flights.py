import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from dependency_injector.wiring import inject, Provide

from ..schemas.flight import FlightResponse
from ...service import Service
from ...container import Container
from ...providers.flights import DateTooOld
from ...providers.airports import AirportsForCountryNotFound, InvalidCountry
from ...settings import SETTINGS


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
        raise HTTPException(status_code=422, detail=_msg)
    except Exception as e:
        service.log.exception("api.get_top_flights.exception")
        raise HTTPException(status_code=500, detail="Unexpected problem on server.")
