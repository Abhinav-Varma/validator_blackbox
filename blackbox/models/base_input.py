from pydantic import BaseModel
from typing import Any, Dict


class RawInput(BaseModel):
    """
    Generic container for the raw input JSON.
    This model intentionally does NOT validate structure.
    """
    data: Dict[str, Any]
