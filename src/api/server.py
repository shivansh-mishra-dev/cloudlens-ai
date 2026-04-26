import logging
import uuid
import json
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from ai._langgraph.build_agent_graph import build_agent_graph
from ai.agent_state import AgentState
from api.schemas.request import ChatStreamRequest, SessionCreateRequest
from ai.session_manager import cache_aws_credentials
from pathlib import Path

logger = logging.getLogger(__name__)
app = FastAPI()


@app.post("/session", description="Initalize AWS Credentials")
async def create_session(req: SessionCreateRequest):
    session_id = str(uuid.uuid4())
    success = cache_aws_credentials(session_id, req.access_key, req.secret_key)

    if not success:
        logger.error(f"Failed to connect to redis.")
        return HTTPException(
            status_code=500, detail="Internal caching layer unavailable."
        )

    return JSONResponse(
        status_code=200,
        content={
            "session_id": session_id,
            "message": "Session created successfully. Credentials cached for 15 minutes.",
        },
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    graph = build_agent_graph()

    async def _event_generator():
        state_update: AgentState = {
            "messages": [HumanMessage(content=req.message)],
            "error_message": None,
            "expanded_intent": None,
            "is_infra_query": False,
            "raw_data": None,
            "session_id": req.session_id,
            "sql_query": None,
        }

        try:
            async for event in graph.astream(
                state_update,
                config={"configurable": {"thread_id": req.session_id}},
                stream_mode="updates",
            ):
                for node_name, node_state in event.items():
                    if node_name == "format":
                        final_msg = node_state["messages"][-1].content
                        payload = {"type": "final_response", "content": final_msg}
                        yield f"data: {json.dumps(payload)}\n\n"

                    else:
                        payload = {"type": "node_status", "node": node_name}
                        yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            error_payload = {
                "type": "error",
                "content": "A fatal error occurred during graph execution.",
            }
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(_event_generator(), media_type="text/event-stream")


BASE_DIR = Path(__file__).resolve().parent.parent

UI_DIST = BASE_DIR / "ui/dist"

if UI_DIST.exists():
    app.mount("/", StaticFiles(directory=UI_DIST, html=True))

else:
    logger.warning(
        f"UI directory not found at {UI_DIST}. Make sure to run 'bun run build' inside src/ui."
    )
