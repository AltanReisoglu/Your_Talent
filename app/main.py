from fastapi import FastAPI

from app.schemas import HealthResponse, InvokeRequest, InvokeResponse
from app.service import invoke_agent, load_local_env

load_local_env()

app = FastAPI(
    title="FinWiki API",
    version="0.1.0",
    description="Thin HTTP runtime for the FinWiki multi-agent financial wiki.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="finwiki-api")


@app.post("/invoke", response_model=InvokeResponse)
def invoke(payload: InvokeRequest) -> InvokeResponse:
    result = invoke_agent(
        message=payload.message,
        user_id=payload.user_id,
        session_id=payload.session_id,
    )
    return InvokeResponse(**result)
