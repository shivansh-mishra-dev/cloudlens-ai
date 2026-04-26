# CloudLens AI: Agentic AWS Infrastructure Assistant

CloudLens AI is a conversational, agentic AI assistant designed to query and audit AWS cloud infrastructure using natural language. 

Instead of writing complex AWS CLI commands or custom Python scripts, users can simply ask questions like, *"List all my public S3 buckets,"* or *"How many EC2 instances are currently running?"* The agent translates these intents into strictly read-only PostgreSQL queries, executes them against the live AWS environment, and formats the results into a conversational response.

## Core Technologies

* **Orchestration (The Brain):** [LangGraph](https://www.langchain.com/langgraph) (Stateful, multi-actor agent orchestration)
* **Data Layer (The Engine):** [Steampipe](https://steampipe.io/) (Zero-ETL tool exposing AWS APIs as a high-performance PostgreSQL database)
* **LLM:** Local `gemma4:e2b` running via [Ollama](https://ollama.com/) (Zero-cost, private inference)
* **Session Management:** Redis (Dockerized) for secure, ephemeral AWS credential caching.

## Architectural Highlights

This project was built with a focus on enterprise-grade architecture, safety, and fault tolerance:

* **Protective Gateway (Guardrails):** The input flows through an Evaluator and Guardrail node. If a user asks a non-infrastructure question (e.g., "Bake a cake"), the graph short-circuits to reject the prompt, preventing prompt injection attacks.
* **LLM-Free Security Firewall:** A deterministic Python `CodeValidator` node inspects the generated SQL. It strictly enforces read-only operations by blocking `DROP`, `DELETE`, `UPDATE`, or `INSERT` statements before they reach the execution layer.
* **Cyclic Self-Correction:** If the generated SQL has a syntax error or fails the security firewall, LangGraph routes the execution *back* to the LLM with the error context, allowing the agent to self-correct and retry.
* **Stateless Execution & Race Condition Prevention:** AWS credentials are not stored in environment variables or configuration files. They are securely cached in Redis with a strict 15-minute Time-To-Live (TTL) using a unique `session_id`, ensuring thread safety and preventing credential leakage across concurrent users.
* **Rolling Window Memory:** Implements a LangGraph `MemorySaver` checkpointer with a sliced context window to maintain conversational history (e.g., *"Sort that last list by date"*) without causing an LLM token blowout.
* **Chain-of-Thought (CoT) Prompting:** The LLM is prompted to output its reasoning in a `<thought_process>` block before generating SQL, drastically reducing syntax errors from the smaller local model.

## Project Structure

```text
.
├── ai
│   ├── agent_state.py
│   ├── __init__.py
│   ├── _langgraph
│   │   ├── build_agent_graph.py
│   │   ├── evaluate_intent_node.py
│   │   ├── execute_sql_node.py
│   │   ├── format_response_node.py
│   │   ├── generate_sql_node.py
│   │   ├── guardrail_node.py
│   │   ├── __init__.py
│   │   └── validate_sql_node.py
│   ├── models
│   │   ├── gemma4_e2b.py
│   │   └── __init__.py
│   ├── prompts.py
│   ├── session_manager.py
│   └── tools
│       ├── execute_aws_sql_query.py
│       └── __init__.py
├── app.py # Dummy file
└── cli
    ├── __init__.py
    ├── __main__.py # Entry point (python -m cli)
    └── run.py # Interactive REPL chat loop

6 directories, 20 files
```

## Prerequisites

1. **Ollama** installed and running locally

```bash
ollama run gemma4:e2b
```

2. **Steampipe** Installed with the AWS plugin configured.
```bash
steampipe plugin install aws
```

3. **Redis** running locally (use the provided docker-commpose.yaml)
```bash
docker compose -f docker/docker-compose.yaml up -d
```

4. **AWS Credentials** A set of AWS Access Keys (Preferably with ReadOnlyAccess IAM permissions attached).


## Installation & Setup

1. Clone the repositoy:
```bash
git clone https://github.com/shivansh-mishra-dev/cloudlens-ai.git
cd cloudlens-ai
```

2. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

or 

```bash
conda env create -f conda-env.yaml
conda activate cloudlens-ai
pip install -r requirements.txt
```


## Usage

Run the application using the Command Line Interface (CLI) module:

```bash
python -m cli
```

Upon startup, you will be securely prompted for your temporary AWS credentials (input is hidden). These are cached in Redis for 15 minutes.

## Example Interaction:
```text
You: List my S3 buckets.

Agent: Thinking...
Agent: Based on the AWS data provided, here are the S3 buckets found:

    * bucket-name (Region: ap-south-1)

You: How many items does the first bucket have?

Agent: Thinking...
Agent: The bucket 'bucket-name' currently contains 42 objects.
```
## Next Steps (Phase 3 & 4)

* FastAPI & SSE Integration: Wrap the LangGraph execution in a FastAPI backend and stream the agent's thought process token-by-token using Server-Sent Events (SSE).

* RAG Schema Injection: Implement a Vector Database to dynamically retrieve and inject Steampipe table schemas into the LLM context, expanding support beyond S3, EC2, and RDS.