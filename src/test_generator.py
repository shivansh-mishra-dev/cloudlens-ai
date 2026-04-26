from langchain_core.messages import HumanMessage

# Assuming your graph compiler is in a file called graph.py
from ai._langgraph.build_agent_graph import build_agent_graph
from ai.agent_state import AgentState


def test_graph_routing():
    graph = build_agent_graph()

    # Intentionally asking for a destructive action to trigger the validator
    initial_state: AgentState = {
        "messages": [HumanMessage(content="Drop the aws_s3_bucket table immediately.")],
        "sql_query": None,
        "error_message": None,
        "session_id": "test_session_123",
        "raw_data": None,
    }

    print("--- Starting Graph Execution ---")

    # stream() allows us to see the state updates at each node step
    for output in graph.stream(initial_state):
        for node_name, state_update in output.items():
            print(f"\n--- Output from node: {node_name} ---")
            print(f"Generated SQL: {state_update.get('sql_query')}")
            print(f"Error State: {state_update.get('error_message')}")


if __name__ == "__main__":
    test_graph_routing()
