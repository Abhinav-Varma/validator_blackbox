from pydantic import BaseModel, model_validator
from blackbox.models.base_input import RawInput


class VisaRules(BaseModel):
    input: RawInput

    visa_type: str = ""
    from_country: str = ""
    to_country: str = ""
    departure_date: str = ""
    arrival_date: str = ""

    @model_validator(mode="after")
    def derive_visa_fields(self):
        visa = self.input.data["visa_request_information"]["visa_request"]

        self.visa_type = visa["visa_type"]
        self.from_country = visa["from_country_full_name"]
        self.to_country = visa["to_country_full_name"]
        self.departure_date = visa["departure_date_formatted"]
        self.arrival_date = visa["arrival_date_formatted"]

        return self
