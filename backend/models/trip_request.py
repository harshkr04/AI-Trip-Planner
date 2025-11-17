from pydantic import BaseModel

class AgentTripRequest(BaseModel):
    prompt: str
    start_date: str
    end_date: str
    destination: str | None = None  # optional, can be parsed from prompt
