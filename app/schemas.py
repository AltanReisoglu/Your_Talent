from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    user_id: str = Field(default="local-user", min_length=1)
    session_id: str = Field(default="default", min_length=1)
    message: str = Field(min_length=1)


class InvokeResponse(BaseModel):
    user_id: str
    session_id: str
    thread_id: str
    response: str


class HealthResponse(BaseModel):
    status: str
    service: str

