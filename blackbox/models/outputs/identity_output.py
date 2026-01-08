from pydantic import BaseModel


class IdentityOutput(BaseModel):
    full_name: str
    passport_number: str
    nationality: str
    date_of_birth: str
