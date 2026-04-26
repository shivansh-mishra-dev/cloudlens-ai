import uuid
import getpass
import os
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from ai.session_manager import cache_aws_credentials
from ai._langgraph.build_agent_graph import build_agent_graph
from ai.agent_state import AgentState

load_dotenv()


def start_chat():
    print("=========================================")
    print("☁️  AWS Steampipe AI Assistant Initialized")
    print("=========================================")

    print("\nTo begin, please provide your temporary AWS credentials.")
    access_key = getpass.getpass("AWS Access Key ID: ")
    secret_key = getpass.getpass("AWS Secret Access Key: ")

    if not access_key or not secret_key:
        print("Error: Credentials cannot be empty. Exiting.")
        return

    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key

    session_id = str(uuid.uuid4())

    cache_success = cache_aws_credentials(session_id, access_key, secret_key)
    if not cache_success:
        print("Fatal Error: Could not connect to Redis to store session. Exiting.")
        return
    print(f"\n[Session Initialized: {session_id}]")
    print("Type 'exit' or 'quit' to stop.\n")

    graph = build_agent_graph()

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Shutting down assistant. Goodbye!")
                break

            if not user_input.strip():
                continue

            initial_state: AgentState = {
                "messages": [HumanMessage(content=user_input)],
                "session_id": session_id,
                "error_message": None,
                "expanded_intent": None,
                "is_infra_query": False,
                "raw_data": None,
                "sql_query": None,
            }

            print("Agent: Thinking...")

            final_state = graph.invoke(
                initial_state, config={"configurable": {"thread_id": session_id}}
            )

            agent_response = final_state["messages"][-1].content
            print(f"\nAgent: {agent_response}\n")

        except KeyboardInterrupt:
            print("\nShutting down assistant. Goodbye!")
            break
        except Exception as e:
            print(f"\n[System Error]: {str(e)}\n")
