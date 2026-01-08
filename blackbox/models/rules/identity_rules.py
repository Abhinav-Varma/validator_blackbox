from pydantic import BaseModel, model_validator
from blackbox.models.base_input import RawInput


class IdentityRules(BaseModel):
    input: RawInput

    full_name: str = ""
    passport_number: str = ""
    nationality: str = ""
    date_of_birth: str = ""

    @model_validator(mode="after")
    def derive_identity_fields(self):
        passport = self.input.data["passport"]["passport_details"]

        self.full_name = f"{passport['first_name']} {passport['surname']}"
        self.passport_number = passport["passport_number"]
        self.nationality = passport["nationality"]
        self.date_of_birth = passport["date_of_birth"]["$date"]

        return self
