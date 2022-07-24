from pydantic import BaseModel


class FlightResponse(BaseModel):
    src: str
    dst: str
    price: str

    class Config:
        schema_extra = {"example": {"src": "ABC", "dst": "CBA", "price": "102.3"}}
