from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    sql_query: Optional[str]
    error_message: Optional[str]
    raw_data: Optional[str]
    expanded_intent: Optional[str]
    is_infra_query: Optional[bool]
    session_id: str
