# 🤖 LangGraph Agentic Chatbot

A multi-turn conversational AI application built with **LangGraph**, **Ollama**, and **Streamlit** — featuring persistent memory, thread-based conversation management, and real-time streaming responses.

---

## 🧠 Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Streamlit Frontend              │
│  - Chat UI with streaming                   │
│  - Sidebar: thread management               │
│  - Session state per conversation           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│           LangGraph Agentic Backend         │
│                                             │
│   ┌──────────┐     ┌──────────────────┐    │
│   │  START   │────▶│   chat_node      │    │
│   └──────────┘     │  (LLM invocation)│    │
│                    └────────┬─────────┘    │
│                             │              │
│                    ┌────────▼─────────┐    │
│                    │      END         │    │
│                    └──────────────────┘    │
│                                             │
│   Checkpointer: SqliteSaver                 │
│   (persists state per thread_id)            │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│           Ollama (Local LLM)                │
│   Model: llama2                             │
│   Runs locally — no API key required        │
└─────────────────────────────────────────────┘
```

---

## ✨ Features

- **Multi-turn memory** — Conversations persist across sessions using SQLite checkpointing
- **Thread management** — Start new chats or switch between past conversations from the sidebar
- **Streaming responses** — Real-time token streaming via LangGraph's `stream_mode="messages"`
- **Local LLM** — Powered by Ollama (llama2), fully offline-capable
- **Agentic graph** — Built on LangGraph's `StateGraph` for extensibility

---

## 📁 Project Structure

```
.
├── langraph_backend.py      # LangGraph graph definition, LLM, checkpointer
├── streamlit_frontend.py    # Streamlit UI, session state, streaming chat
├── ollama_check.py          # Quick sanity check for Ollama connectivity
├── config.py                # Model name, API keys, service account config
├── chatbot_checkpoints.db   # SQLite DB (auto-created at runtime)
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Install dependencies

```bash
pip install langgraph langchain-core langchain-ollama streamlit python-dotenv
```

### 3. Pull the LLM model via Ollama

```bash
ollama pull llama2
```

### 4. Verify Ollama is working

```bash
python ollama_check.py
```

You should see a one-line explanation of AI printed to the terminal.

### 5. Configure environment

Create a `.env` file or update `config.py`:

```python
# config.py
MODEL_NAME = "llama2"
API_KEY = ""                    # Not required for Ollama
SERVICE_ACCOUNT_FILE = ""       # Only needed for Vertex AI
```

### 6. Run the app

```bash
streamlit run streamlit_frontend.py
```

---

## 🗺️ How It Works

### State Management

The graph uses a `TypedDict` state with `add_messages` reducer — new messages are appended rather than overwritten, enabling natural multi-turn conversation:

```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

### Checkpointing

Each conversation thread is identified by a `thread_id` (UUID). LangGraph's `SqliteSaver` persists the full message history to `chatbot_checkpoints.db`, so conversations survive app restarts.

```python
config = {"configurable": {"thread_id": "<uuid>"}}
chatbot.stream({"messages": [HumanMessage(...)]}, config=config)
```

### Streaming

Responses are streamed token-by-token using `stream_mode="messages"`, rendered live in the Streamlit UI via `st.write_stream`.

---

## 🔁 Switching to Vertex AI (Optional)

The backend includes commented-out Vertex AI support. To enable it:

1. Set up a Google Cloud service account with Vertex AI permissions
2. Update `config.py` with your `SERVICE_ACCOUNT_FILE` path and `MODEL_NAME`
3. In `langraph_backend.py`, uncomment the `ChatVertexAI` block and comment out the `ChatOllama` block

---

## 🛠️ Extending the Graph

LangGraph makes it straightforward to add new capabilities:

```python
# Add a tool-calling node
graph.add_node("tool_node", tool_executor)
graph.add_conditional_edges("chat_node", route_to_tools, {...})
```

Possible extensions: web search, RAG retrieval, document summarization, HITL (Human-in-the-Loop) with interrupt nodes.

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `langgraph` | Agentic graph orchestration & checkpointing |
| `langchain-core` | Message types (`HumanMessage`, `BaseMessage`) |
| `langchain-ollama` | Ollama LLM integration |
| `streamlit` | Frontend UI |
| `python-dotenv` | Environment variable management |

---

## 📝 License

MIT
