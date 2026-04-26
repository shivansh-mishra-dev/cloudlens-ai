from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    access_key: str
    secret_key: str


class ChatStreamRequest(BaseModel):
    session_id: str
    message: str
