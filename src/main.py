from pydantic import BaseModel, Field
from src.transform import transformer

class OutputModel(BaseModel):
    full_name: str = Field(
        default_factory=lambda: transformer("CONCATENATE(CAPITALIZE('john'), CAPITALIZE('doe'))"),
        description="Full name of the customer"
    )

# Example usage
if __name__ == "__main__":
    output = OutputModel()
    print("Final Full Name:", output.full_name)  # Expected Output: "John Doe"
