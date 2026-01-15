from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class MessagePayload(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str
    ts: str  # ISO8601 UTC string
    text: Optional[str] = Field(None, max_length=4096)

    @validator("ts")
    def validate_ts(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("ts must be ISO8601 UTC string")
        return v
