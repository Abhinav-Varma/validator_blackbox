from pydantic import BaseModel


class AddressEmploymentOutput(BaseModel):
    city: str
    state: str
    country: str
    occupation: str
    employer_name: str
