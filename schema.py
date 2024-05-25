import pydantic
from typing import Optional


class CreateTicket(pydantic.BaseModel):
    header: str
    description: str
    owner: str


class UpdateTicket(pydantic.BaseModel):
    header: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None

