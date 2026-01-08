from pydantic import BaseModel


class VisaOutput(BaseModel):
    visa_type: str
    from_country: str
    to_country: str
    departure_date: str
    arrival_date: str

    @validator('departure_date', 'arrival_date')
    def check_date_format(cls, value):
        try:
            # Validate the date format
            datetime.strptime(value, "%d-%b-%Y")
        except ValueError:
            raise ValueError('Date must be in the format DD-Mon-YYYY')
        return value