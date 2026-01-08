import json
from blackbox.engine.orchestrator import run_all_transformations

with open("blackbox\input\sample_record.json", "r") as f:
    input_data = json.load(f)

outputs = run_all_transformations(input_data)

print(json.dumps(outputs, indent=2))
