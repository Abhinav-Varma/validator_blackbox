from pydantic import BaseModel


class VisaOutput(BaseModel):
    visa_type: str
    from_country: str
    to_country: str
    departure_date: str
    arrival_date: str
