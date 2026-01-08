import json
from blackbox.models.base_input import RawInput
from blackbox.models.rules.identity_rules import IdentityRules
from blackbox.models.rules.visa_rules import VisaRules
from blackbox.models.rules.address_employment_rules import AddressEmploymentRules


def run_all_transformations(input_data: dict):
    raw = RawInput(data=input_data)

    identity = IdentityRules(input=raw)
    visa = VisaRules(input=raw)
    address = AddressEmploymentRules(input=raw)

    return {
        "identity_output": identity.model_dump(exclude={"input"}),
        "visa_output": visa.model_dump(exclude={"input"}),
        "address_employment_output": address.model_dump(exclude={"input"}),
    }
