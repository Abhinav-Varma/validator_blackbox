from pydantic import BaseModel, model_validator
from blackbox.models.base_input import RawInput


class AddressEmploymentRules(BaseModel):
    input: RawInput

    city: str = ""
    state: str = ""
    country: str = ""
    occupation: str = ""
    employer_name: str = ""

    @model_validator(mode="after")
    def derive_address_employment_fields(self):
        address = self.input.data["residential_address"]["residential_address_card_v2"]
        work = self.input.data["work_address"]["work_details"]

        self.city = address["city"]
        self.state = address["state"]
        self.country = address["country"]
        self.occupation = work["occupation"]
        self.employer_name = work["employer_name"]

        return self
