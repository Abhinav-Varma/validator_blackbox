# src/main.py
import json
from src.custom_basemodel import TransformBaseModel

# Define the output model using custom base model
class OutputModel(TransformBaseModel):
    full_name: str = TransformBaseModel.TransformField(
        description="Full name of the customer",
        function_logic="CONCATENATE(CAPITALIZE($..first_name), CAPITALIZE($..last_name))"
    )

# Example usage
if __name__ == "__main__":
    # Load JSON data from file
    with open('sample.json', 'r') as f:
        json_data = json.load(f)
    
    # Create model instance with automatic transformation
    output = OutputModel(json_data=json_data)
    
    print("Final Full Name:", output.full_name)  # Expected Output: "John . Doe"