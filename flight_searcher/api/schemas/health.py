from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str

    class Config:
        schema_extra = {"example": {"status": "ok"}}
