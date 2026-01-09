from pydantic import BaseModel, constr, validator
from datetime import datetime

class IdentityOutput(BaseModel):
    full_name: constr(min_length=1, max_length=256)
    passport_number: constr(pattern=r'^[A-Z][0-9]{7}$')
    nationality: str
    date_of_birth: str

    @validator('date_of_birth')
    def check_date_format(cls, value):
        try:
            # Validate the date format
            datetime.strptime(value, "%d-%b-%Y")
        except ValueError:
            raise ValueError('Date must be in the format DD-Mon-YYYY')
        return value
