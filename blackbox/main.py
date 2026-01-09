import json
from blackbox.engine.orchestrator import run_all_transformations
from blackbox.models.outputs.identity_output import IdentityOutput
from blackbox.models.outputs.visa_output import VisaOutput
from blackbox.models.outputs.address_employment_output import AddressEmploymentOutput

with open(r"./blackbox/input/sample_record.json", "r") as f:
    input_data = json.load(f)

outputs = run_all_transformations(input_data)

identity = IdentityOutput(**outputs['identity_output'])
visa = VisaOutput(**outputs['visa_output'])
address = AddressEmploymentOutput(**outputs['address_employment_output'])

print(json.dumps(outputs, indent=2))
