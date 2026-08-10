from pydantic import BaseModel


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    answer: str
    tools_used: list[str] = []
    sources: list[str] = []


class LeadRequest(BaseModel):
    company_name: str
    contact_name: str | None = None
    industry: str | None = None
    size: str | None = None


class LeadResponse(BaseModel):
    instance_key: int | None = None
    status: str
    message: str
