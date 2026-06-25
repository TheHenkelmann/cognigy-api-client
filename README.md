# Cognigy API Client (Python)

[![PyPI version](https://img.shields.io/pypi/v/cognigy-api-client)](https://pypi.org/project/cognigy-api-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/cognigy-api-client)](https://pypi.org/project/cognigy-api-client/)
[![License: MIT](https://img.shields.io/github/license/TheHenkelmann/cognigy-api-client)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/TheHenkelmann/cognigy-api-client/ci.yml?branch=master)](https://github.com/TheHenkelmann/cognigy-api-client/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/TheHenkelmann/cognigy-api-client/branch/master/graph/badge.svg)](https://codecov.io/gh/TheHenkelmann/cognigy-api-client)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/TheHenkelmann/cognigy-api-client)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **Disclaimer:** This is an **unofficial, community-maintained** Python client for the [Cognigy.AI](https://www.cognigy.com/) REST API. It is **not** affiliated with, endorsed by, or supported by Cognigy GmbH. For official client libraries, see [Cognigy's documentation](https://docs.cognigy.com/ai/for-developers/developers/client-libraries).

A modern, strictly typed Python SDK for the Cognigy.AI REST API. It provides synchronous and asynchronous clients, Pydantic models for request/response validation, and resource-oriented access to projects, flows, nodes, AI agents, analytics, conversations, knowledge stores, locales, logs, tasks, search, and snapshots.

**Features**

- Strictly typed with Pydantic v2 models and `py.typed` marker
- Sync (`CognigyClient`) and async (`AsyncCognigyClient`) clients
- Resource-oriented API covering projects, flows, nodes, AI agents, knowledge stores, snapshots, and more
- Pagination helpers, validation utilities, and structured error types
- CI with linting, formatting, type checking, and tests across Python 3.9–3.13

See the [changelog](CHANGELOG.md) for release history.

## Installation

```bash
pip install cognigy-api-client
```

The import name remains `cognigy`:

```python
from cognigy import CognigyClient
```

**Requirements:** Python 3.9+, `httpx>=0.24.0`, `pydantic>=2.0.0`.

### Development

```bash
git clone https://github.com/TheHenkelmann/cognigy-api-client.git
cd cognigy-api-client
pip install -e ".[dev]"
pytest --cov=cognigy
ruff check src tests
ruff format --check src tests
MYPYPATH=.mypy_stubs mypy -p cognigy  # after: mkdir -p .mypy_stubs && ln -sfn ../src .mypy_stubs/cognigy
pre-commit install
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## General Usage

### Synchronous client

Create a client with your API key (or set the `COGNIGY_API_KEY` environment variable). Optionally set `COGNIGY_BASE_URL` (default: `https://api-app.cognigy.ai`).

```python
from cognigy import CognigyClient

client = CognigyClient(api_key="your-api-key")
# or: client = CognigyClient()  # uses COGNIGY_API_KEY

projects = client.projects.list()
for project in projects:
    print(f"{project.name} (ID: {project.id})")

client.close()  # remember to close when done
```

Using a context manager (recommended):

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    projects = client.projects.list()
    print(projects)
```

### Asynchronous client

For non-blocking I/O, use `AsyncCognigyClient` with async resource methods:

```python
import asyncio
from cognigy import AsyncCognigyClient

async def main():
    async with AsyncCognigyClient(api_key="your-api-key") as client:
        projects = await client.projects.list()
        for project in projects:
            print(project.name)

asyncio.run(main())
```

### Configuration

| Option   | Constructor   | Environment variable | Default                        |
| -------- | ------------- | -------------------- | ------------------------------ |
| API key  | `api_key=`  | `COGNIGY_API_KEY`  | (required)                     |
| Base URL | `base_url=` | `COGNIGY_BASE_URL` | `https://api-app.cognigy.ai` |
| Timeout  | `timeout=`  | —                   | `60` seconds                 |

### Exceptions

- `CognigyConfigurationError` — invalid or missing configuration (e.g. no API key).
- `CognigyAPIError` — API request failed; has `message`, `status_code`, and `response_body`.

---

## Models

All API request/response payloads are represented as PydanticV2 models under `cognigy.models`. They support validation, serialization with `model_dump(by_alias=True)`, and automatic `_id` → `id` mapping via the base class.

| Module / domain               | Models                                                                                                                                                                      |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Base**                | `CognigyBaseModel`                                                                                                                                                        |
| **Project**             | `Project`, `ProjectCreate`, `ProjectUpdate`, `HandoverConfiguration`, `CssColor`, `CognigyColor`, `ProjectLocale`, `WhisperAssistConfiguration`             |
| **Flow**                | `Flow`, `FlowCreate`, `FlowUpdate`, `FeedbackReport`, `FeedbackReportFinding`, `FeedbackReportInfo`, `LowDataIntent`                                          |
| **AI Agent**            | `AIAgent`, `AIAgentCreate`, `AIAgentUpdate`, `AIAgentJob`, `AIAgentTool`, `AIAgentValidateNameRequest`, `SpeakingStyle`, `VoiceConfigs`, `SafetySettings` |
| **Node**                | `Node`, `NodeCreate`, `NodeUpdate`, `NodeMock`, `Chart`, `ChartNodeSummary`, `ChartRelation`                                                         |
| **Analytics**           | `CallCounterMetric`, `ConversationCounterMetric`, `ChannelConversations`                                                                                              |
| **Conversation**        | `Conversation`, `ConversationMessage`                                                                                                                                   |
| **Knowledge Store**     | `KnowledgeStore`, `KnowledgeStoreCreate`, `KnowledgeStoreUpdate`, `KnowledgeStoreStatus`                                                                            |
| **Knowledge Chunk**     | `KnowledgeChunk`, `KnowledgeChunkCreate`, `KnowledgeChunkUpdate`                                                                                                      |
| **Knowledge Source**    | `KnowledgeSource`, `KnowledgeSourceCreate`, `KnowledgeSourceUpdate`, `KnowledgeSourceType`, `KnowledgeSourceStatus`, `KnowledgeSourceMetaData`                  |
| **Knowledge Connector** | `KnowledgeConnector`, `KnowledgeConnectorCreate`, `KnowledgeConnectorUpdate`, `KnowledgeConnectorExecutionStatus`, `ConnectorSchedule`                            |
| **Locale**              | `Locale`, `LocaleCreate`, `LocaleUpdate`, `NluLanguage`                                                                                                             |
| **Log**                 | `LogEntry`                                                                                                                                                                |
| **Task**                | `Task`, `TaskStatus`                                                                                                                                                    |
| **Search**              | `SearchResult`, `SearchResultType`, `NLUConnectorSubType`, `EndpointSubType`, `GenerativeAIProviderSubType`                                                       |
| **Snapshot**            | `Snapshot`, `SnapshotCreate`, `SnapshotResource`, `SnapshotDownloadLink`, `SnapshotRestoreRequest`, `SnapshotDownloadLinkRequest`                               |
| **Connection**          | `Connection`, `ConnectionCreate`, `ConnectionUpdate`, `ConnectionListItem`, `ConnectionSchemaItem`, `ConnectionSchemaRef`, `ConnectionFieldCreate`, `ConnectionBatchRequest`, `ConnectionBatchResult`, `ConnectionBatchCreateOp`, `ConnectionBatchUpdateOp`, `ConnectionBatchDeleteOp`, `ConnectionBatchCreateValue`, `ConnectionBatchUpdateValue`, `ConnectionBatchOperation`, `ResourceLevel` |

Import from the top-level package or from `cognigy.models`:

```python
from cognigy import ProjectCreate, Flow, AIAgentCreate
# or
from cognigy.models import ProjectCreate, Flow, AIAgentCreate
```

---

## Resources

The client exposes one resource object per API domain. All resources are available as `client.<resource_name>` (e.g. `client.projects`, `client.flows`). Each section below lists the **synchronous** methods; async resources (used with `AsyncCognigyClient`) expose the same methods as `async` and are awaited.

---

### Projects (`client.projects`)

Top-level containers for flows, intents, lexicons, endpoints, etc.

| Method                       | Description       | Example                                                                                 |
| ---------------------------- | ----------------- | --------------------------------------------------------------------------------------- |
| `list()`                   | List all projects | `projects = client.projects.list()`                                                   |
| `create(data)`             | Create a project  | `project = client.projects.create(ProjectCreate(name="My Bot", color="cognigyBlue"))` |
| `get(project_id)`          | Get project by ID | `project = client.projects.get("507f1f77bcf86cd799439011")`                           |
| `update(project_id, data)` | Update a project  | `project = client.projects.update("507f…", ProjectUpdate(name="New Name"))`          |
| `delete(project_id)`       | Delete a project  | `client.projects.delete("507f1f77bcf86cd799439011")`                                  |

**Example:**

```python
from cognigy import CognigyClient, ProjectCreate, ProjectLocale

with CognigyClient(api_key="your-api-key") as client:
    new_project = ProjectCreate(
        name="Customer Support Bot",
        color="cognigyBlue",
        locale=ProjectLocale.EN_US,
    )
    project = client.projects.create(new_project)
    print(f"Created: {project.id}")

    project = client.projects.get(project.id)
    project = client.projects.update(project.id, ProjectUpdate(name="Support Bot v2"))
```

---

### Flows (`client.flows`)

Conversation flows within a project.

| Method                                 | Description                                                                                        | Example                                                                      |
| -------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `list(...)`                          | List flows (optional:`project_id`, `filter`, `with_ai_agents`, `limit`, `sort`, cursors) | `flows = client.flows.list(project_id="507f…")`                           |
| `create(data)`                       | Create a flow                                                                                      | `flow = client.flows.create(FlowCreate(name="Main", project_id="507f…"))` |
| `get(flow_id, preferred_locale_id?)` | Get flow by ID                                                                                     | `flow = client.flows.get("507f1f77bcf86cd799439011")`                      |
| `update(flow_id, data)`              | Update a flow                                                                                      | `flow = client.flows.update("507f…", FlowUpdate(description="Updated"))`  |
| `delete(flow_id)`                    | Delete a flow                                                                                      | `client.flows.delete("507f1f77bcf86cd799439011")`                          |

**Example:**

```python
from cognigy import CognigyClient, FlowCreate, FlowUpdate

with CognigyClient(api_key="your-api-key") as client:
    flows = client.flows.list(project_id="507f1f77bcf86cd799439011", limit=10)
    flow = client.flows.create(FlowCreate(name="Onboarding", project_id="507f…"))
    flow = client.flows.get(flow.id)
    flow = client.flows.update(flow.id, FlowUpdate(name="Onboarding v2"))
```

---

### Nodes (`client.nodes`)

Chart nodes and flow topology. Nodes belong to a flow.

| Method                                                  | Description                            | Example                                                                                                                                     |
| ------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_all(flow_id)`                                    | All nodes with topology merged         | `nodes = client.nodes.get_all("507f…")`                                                                                                  |
| `list(flow_id, limit?, next?, previous?)`             | List nodes (paginated)                 | `nodes = client.nodes.list("507f…", limit=50)`                                                                                           |
| `get(flow_id, node_id, include_conversion_metadata?)` | Get one node                           | `node = client.nodes.get("507f…", "507f…")`                                                                                             |
| `create(flow_id, data)`                               | Create a node                          | `node = client.nodes.create("507f…", NodeCreate(type="say", target="507f…", mode="appendChild", label="Hi", config={"text": "Hello"}))` |
| `update(flow_id, node_id, data)`                      | Update a node                          | `node = client.nodes.update("507f…", "507f…", NodeUpdate(label="Greeting"))`                                                            |
| `delete(flow_id, node_id)`                            | Delete a node                          | `client.nodes.delete("507f…", "507f…")`                                                                                                 |
| `get_chart(flow_id)`                                  | Get chart topology (nodes + relations) | `chart = client.nodes.get_chart("507f…")`                                                                                                |

**Example:**

```python
from cognigy import CognigyClient, NodeCreate, NodeUpdate

with CognigyClient(api_key="your-api-key") as client:
    flow_id = "507f1f77bcf86cd799439011"
    nodes = client.nodes.get_all(flow_id)
    chart = client.nodes.get_chart(flow_id)
    new_node = client.nodes.create(flow_id, NodeCreate(
        type="say", target=nodes[0].id, mode="appendChild",
        label="Greeting", config={"text": "Hello!"}
    ))
    client.nodes.update(flow_id, new_node.id, NodeUpdate(label="Welcome"))
```

---

### AI Agents (`client.aiagents`)

AI agents and their jobs/tools.

| Method                                                  | Description                       | Example                                                                               |
| ------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------- |
| `list(project_id?, filter?, limit?, sort?, cursors?)` | List AI agents                    | `agents = client.aiagents.list(project_id="507f…")`                                |
| `create(data)`                                        | Create an AI agent                | `agent = client.aiagents.create(AIAgentCreate(name="Helper", project_id="507f…"))` |
| `get(ai_agent_id)`                                    | Get agent by ID                   | `agent = client.aiagents.get("507f1f77bcf86cd799439011")`                           |
| `update(ai_agent_id, data)`                           | Update an AI agent                | `agent = client.aiagents.update("507f…", AIAgentUpdate(description="Updated"))`    |
| `delete(ai_agent_id)`                                 | Delete an AI agent                | `client.aiagents.delete("507f1f77bcf86cd799439011")`                                |
| `get_jobs(ai_agent_id)`                               | List jobs and tools for the agent | `jobs = client.aiagents.get_jobs("507f…")`                                         |
| `validate_name(name, project_id)`                     | Check if name is available        | `client.aiagents.validate_name("My Agent", "507f…")`                               |

**Example:**

```python
from cognigy import CognigyClient, AIAgentCreate, AIAgentUpdate

with CognigyClient(api_key="your-api-key") as client:
    agents = client.aiagents.list(project_id="507f1f77bcf86cd799439011")
    agent = client.aiagents.create(AIAgentCreate(
        name="Support Agent",
        project_id="507f…",
        description="Handles FAQs"
    ))
    jobs = client.aiagents.get_jobs(agent.id)
    client.aiagents.validate_name("New Agent", "507f…")
    client.aiagents.update(agent.id, AIAgentUpdate(name="Support Agent v2"))
```

---

### Analytics (`client.analytics`)

Read-only call and conversation metrics (v3.0 API).

| Method                                                   | Description                           | Example                                                                             |
| -------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------- |
| `list_call_counter(year, month?, project_id?)`         | Call counter metrics (org or project) | `metrics = client.analytics.list_call_counter(2024, month=1)`                     |
| `list_conversation_counter(year, month?, project_id?)` | Conversation counter metrics          | `metrics = client.analytics.list_conversation_counter(2024, project_id="507f…")` |

**Example:**

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    call_metrics = client.analytics.list_call_counter(year=2024, month=1)
    for m in call_metrics:
        print(f"{m.year}-{m.month:02d}-{m.day:02d}: {m.processed_calls} processed")

    conv_metrics = client.analytics.list_conversation_counter(
        year=2024, project_id="507f1f77bcf86cd799439011"
    )
```

---

### Conversations (`client.conversations`)

Conversation list and message history by session.

| Method                 | Description                 | Example                                                  |
| ---------------------- | --------------------------- | -------------------------------------------------------- |
| `list()`             | List conversation summaries | `convs = client.conversations.list()`                  |
| `get(session_id)`    | Get messages for a session  | `messages = client.conversations.get("my-session-id")` |
| `delete(session_id)` | Delete a conversation       | `client.conversations.delete("my-session-id")`         |

**Example:**

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    conversations = client.conversations.list()
    messages = client.conversations.get("abc-session-123")
    for msg in messages:
        print(msg.source, msg.input_text)
```

---

### Knowledge Stores (`client.knowledge_stores`)

Knowledge stores (containers for sources and chunks).

| Method                                         | Description              | Example                                                                                            |
| ---------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------- |
| `list(project_id?, limit?, sort?, cursors?)` | List knowledge stores    | `stores = client.knowledge_stores.list(project_id="507f…")`                                     |
| `create(data)`                               | Create a knowledge store | `store = client.knowledge_stores.create(KnowledgeStoreCreate(name="Docs", project_id="507f…"))` |
| `get(knowledge_store_id)`                    | Get store by ID          | `store = client.knowledge_stores.get("507f1f77bcf86cd799439011")`                                |
| `update(knowledge_store_id, data)`           | Update a store           | `store = client.knowledge_stores.update("507f…", KnowledgeStoreUpdate(name="Docs v2"))`         |
| `delete(knowledge_store_id)`                 | Delete a store           | `client.knowledge_stores.delete("507f1f77bcf86cd799439011")`                                     |

**Example:**

```python
from cognigy import CognigyClient, KnowledgeStoreCreate, KnowledgeStoreUpdate

with CognigyClient(api_key="your-api-key") as client:
    stores = client.knowledge_stores.list(project_id="507f1f77bcf86cd799439011")
    store = client.knowledge_stores.create(KnowledgeStoreCreate(
        name="Product Documentation",
        project_id="507f…",
        description="FAQs and guides"
    ))
    store = client.knowledge_stores.get(store.id)
    client.knowledge_stores.update(store.id, KnowledgeStoreUpdate(description="Updated"))
```

---

### Knowledge Sources (`client.knowledge_sources`)

Sources within a knowledge store (e.g. URL or extension). Path: `knowledgestores/{storeId}/sources`.

| Method                                          | Description             | Example                                                                                                                                    |
| ----------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `list(knowledge_store_id, limit?, cursors?)`  | List sources in a store | `sources = client.knowledge_sources.list("507f…")`                                                                                      |
| `create(knowledge_store_id, data)`            | Create a source         | `source = client.knowledge_sources.create("507f…", KnowledgeSourceCreate(name="Docs", type=KnowledgeSourceType.URL, url="https://…"))` |
| `get(knowledge_store_id, source_id)`          | Get source by ID        | `source = client.knowledge_sources.get("507f…", "507f…")`                                                                              |
| `update(knowledge_store_id, source_id, data)` | Update a source         | `source = client.knowledge_sources.update("507f…", "507f…", KnowledgeSourceUpdate(name="Docs v2"))`                                    |
| `delete(knowledge_store_id, source_id)`       | Delete a source         | `client.knowledge_sources.delete("507f…", "507f…")`                                                                                    |

**Example:**

```python
from cognigy import CognigyClient, KnowledgeSourceCreate, KnowledgeSourceType

with CognigyClient(api_key="your-api-key") as client:
    store_id = "507f1f77bcf86cd799439011"
    sources = client.knowledge_sources.list(store_id)
    source = client.knowledge_sources.create(store_id, KnowledgeSourceCreate(
        name="Documentation",
        type=KnowledgeSourceType.URL,
        url="https://docs.example.com/guide"
    ))
    source = client.knowledge_sources.get(store_id, source.id)
```

---

### Knowledge Chunks (`client.knowledge_chunks`)

Chunks within a knowledge source. Path: `knowledgestores/{storeId}/sources/{sourceId}/chunks`.

| Method                                                    | Description     | Example                                                                                                           |
| --------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------- |
| `list(knowledge_store_id, source_id, limit?, cursors?)` | List chunks     | `chunks = client.knowledge_chunks.list("507f…", "507f…")`                                                     |
| `create(knowledge_store_id, source_id, data)`           | Create a chunk  | `chunk = client.knowledge_chunks.create("507f…", "507f…", KnowledgeChunkCreate(order=1, text="Paragraph…"))` |
| `get(knowledge_store_id, source_id, chunk_id)`          | Get chunk by ID | `chunk = client.knowledge_chunks.get("507f…", "507f…", "507f…")`                                             |
| `update(knowledge_store_id, source_id, chunk_id, data)` | Update a chunk  | `chunk = client.knowledge_chunks.update("507f…", "507f…", "507f…", KnowledgeChunkUpdate(text="Updated"))`    |
| `delete(knowledge_store_id, source_id, chunk_id)`       | Delete a chunk  | `client.knowledge_chunks.delete("507f…", "507f…", "507f…")`                                                  |

**Example:**

```python
from cognigy import CognigyClient, KnowledgeChunkCreate, KnowledgeChunkUpdate

with CognigyClient(api_key="your-api-key") as client:
    store_id, source_id = "507f…", "507f…"
    chunks = client.knowledge_chunks.list(store_id, source_id)
    chunk = client.knowledge_chunks.create(store_id, source_id, KnowledgeChunkCreate(
        order=1, text="This is a paragraph from an article"
    ))
    client.knowledge_chunks.update(store_id, source_id, chunk.id, KnowledgeChunkUpdate(text="Updated text"))
```

---

### Knowledge Connectors (`client.knowledge_connectors`)

Connectors for syncing external data into a knowledge store.

| Method                                                       | Description         | Example                                                                                                                                                                        |
| ------------------------------------------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `list(knowledge_store_id, limit?, skip?, sort?, cursors?)` | List connectors     | `connectors = client.knowledge_connectors.list("507f…")`                                                                                                                    |
| `create(knowledge_store_id, data)`                         | Create a connector  | `conn = client.knowledge_connectors.create("507f…", KnowledgeConnectorCreate(name="Confluence", extension="confluence", version="1.1.0", type="MyConnector", config={…}))` |
| `get(knowledge_store_id, connector_id)`                    | Get connector by ID | `conn = client.knowledge_connectors.get("507f…", "507f…")`                                                                                                                 |
| `update(knowledge_store_id, connector_id, data)`           | Update a connector  | `conn = client.knowledge_connectors.update("507f…", "507f…", KnowledgeConnectorUpdate(name="Confluence v2"))`                                                              |
| `delete(knowledge_store_id, connector_id)`                 | Delete a connector  | `client.knowledge_connectors.delete("507f…", "507f…")`                                                                                                                     |

**Example:**

```python
from cognigy import CognigyClient, KnowledgeConnectorCreate, ConnectorSchedule

with CognigyClient(api_key="your-api-key") as client:
    store_id = "507f1f77bcf86cd799439011"
    connectors = client.knowledge_connectors.list(store_id)
    schedule = ConnectorSchedule(enabled=True, hour=2, minute=0, week_days=[0, 2, 4])
    conn = client.knowledge_connectors.create(store_id, KnowledgeConnectorCreate(
        name="Confluence Sync",
        extension="confluence",
        version="1.1.0",
        type="MyConfluenceConnector",
        config={"baseUrl": "https://wiki.example.com"},
        schedule=schedule
    ))
```

---

### Locales (`client.locales`)

Project locales (language configurations).

| Method                                                  | Description      | Example                                                                                                              |
| ------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `list(project_id?, filter?, limit?, sort?, cursors?)` | List locales     | `locales = client.locales.list(project_id="507f…")`                                                               |
| `create(data)`                                        | Create a locale  | `locale = client.locales.create(LocaleCreate(name="German", project_id="507f…", nlu_language=NluLanguage.DE_DE))` |
| `get(locale_id)`                                      | Get locale by ID | `locale = client.locales.get("507f1f77bcf86cd799439011")`                                                          |
| `update(locale_id, data)`                             | Update a locale  | `locale = client.locales.update("507f…", LocaleUpdate(name="Deutsch"))`                                           |
| `delete(locale_id)`                                   | Delete a locale  | `client.locales.delete("507f1f77bcf86cd799439011")`                                                                |

**Example:**

```python
from cognigy import CognigyClient, LocaleCreate, LocaleUpdate, NluLanguage

with CognigyClient(api_key="your-api-key") as client:
    locales = client.locales.list(project_id="507f1f77bcf86cd799439011")
    locale = client.locales.create(LocaleCreate(
        name="German",
        project_id="507f…",
        nlu_language=NluLanguage.DE_DE
    ))
    client.locales.update(locale.id, LocaleUpdate(name="Deutsch"))
```

---

### Logs (`client.logs`)

Read-only project log entries (flow execution and system events).

| Method                                 | Description               | Example                                             |
| -------------------------------------- | ------------------------- | --------------------------------------------------- |
| `list(project_id, limit?, cursors?)` | List log entries          | `entries = client.logs.list(project_id="507f…")` |
| `get(project_id, log_entry_id)`      | Get log entry by ID       | `entry = client.logs.get("507f…", "507f…")`     |
| `tail(project_id, limit?, cursors?)` | Latest log entries (tail) | `entries = client.logs.tail(project_id="507f…")` |

**Example:**

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    logs = client.logs.list(project_id="507f1f77bcf86cd799439011", limit=50)
    for log in logs:
        print(f"{log.timestamp}: {log.msg}")
    latest = client.logs.tail(project_id="507f1f77bcf86cd799439011")
```

---

### Tasks (`client.tasks`)

Background tasks (e.g. from imports, exports, training). List, get, cancel.

| Method                                                | Description    | Example                                                 |
| ----------------------------------------------------- | -------------- | ------------------------------------------------------- |
| `list(project_id?, limit?, skip?, sort?, cursors?)` | List tasks     | `tasks = client.tasks.list(project_id="507f…")`      |
| `get(task_id)`                                      | Get task by ID | `task = client.tasks.get("507f1f77bcf86cd799439011")` |
| `cancel(task_id)`                                   | Cancel a task  | `client.tasks.cancel("507f1f77bcf86cd799439011")`     |

**Example:**

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    tasks = client.tasks.list(project_id="507f1f77bcf86cd799439011", sort="-createdAt")
    for task in tasks:
        if task.is_running:
            print(f"{task.name}: {task.progress_percent}%")
    task = client.tasks.get("507f1f77bcf86cd799439011")
    client.tasks.cancel(task.id)
```

---

### Search (`client.search`)

Global search across flows, projects, endpoints, etc.

| Method                                                    | Description               | Example                                                           |
| --------------------------------------------------------- | ------------------------- | ----------------------------------------------------------------- |
| `search(query?, project_id?, types?, limit?, cursors?)` | Global search             | `results = client.search.search(query="pizza", types=["flow"])` |
| `list(...)`                                             | Alias for `search(...)` | `results = client.search.list(project_id="507f…")`             |

**Example:**

```python
from cognigy import CognigyClient

with CognigyClient(api_key="your-api-key") as client:
    results = client.search.search(types=["flow"])
    for r in results:
        print(f"{r.name} ({r.type})")
    results = client.search.search(
        query="pizza",
        project_id="507f1f77bcf86cd799439011"
    )
```

---

### Snapshots (`client.snapshots`)

Project snapshots (create, package, download, restore). Many operations return a `Task` for background work.

| Method                                                  | Description                                    | Example                                                                            |
| ------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| `list(project_id?, filter?, limit?, sort?, cursors?)` | List snapshots                                 | `snapshots = client.snapshots.list(project_id="507f…")`                         |
| `create(data)`                                        | Create snapshot (returns `Task`)             | `task = client.snapshots.create(SnapshotCreate(name="v1", project_id="507f…"))` |
| `get(snapshot_id)`                                    | Get snapshot by ID                             | `snapshot = client.snapshots.get("507f1f77bcf86cd799439011")`                    |
| `delete(snapshot_id)`                                 | Delete snapshot (returns `Task`)             | `task = client.snapshots.delete("507f…")`                                       |
| `get_resources(snapshot_id, limit?, sort?, cursors?)` | List resources in snapshot                     | `resources = client.snapshots.get_resources("507f…")`                           |
| `package(snapshot_id)`                                | Package for download (returns `Task`)        | `task = client.snapshots.package("507f…")`                                      |
| `create_download_link(snapshot_id, project_id?)`      | Get download URL for packaged snapshot         | `link = client.snapshots.create_download_link("507f…")`                         |
| `restore(snapshot_id, project_id)`                    | Restore snapshot to project (returns `Task`) | `task = client.snapshots.restore("507f…", "507f…")`                            |

**Example:**

```python
from cognigy import CognigyClient, SnapshotCreate

with CognigyClient(api_key="your-api-key") as client:
    snapshots = client.snapshots.list(project_id="507f1f77bcf86cd799439011")
    task = client.snapshots.create(SnapshotCreate(
        name="Version 1.0",
        description="Release",
        project_id="507f…"
    ))
    snapshot = client.snapshots.get("507f1f77bcf86cd799439011")
    resources = client.snapshots.get_resources(snapshot.id)
    task = client.snapshots.package(snapshot.id)
    link = client.snapshots.create_download_link(snapshot.id)
    print(link.download_link)
    task = client.snapshots.restore(snapshot.id, "507f…")
```

---

### Connections (`client.connections`)

Project and organisation Connections (third-party credentials and settings used by extensions/nodes), including per-Connection fields and Connection schemas.

| Method                                                                  | Description                                  | Example                                                                                                          |
| ----------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `list(project_id?, filter?, limit?, sort?, cursors?, resource_level?)` | List Connections                             | `conns = client.connections.list(project_id="507f…")`                                                         |
| `create(data)`                                                        | Create a Connection                          | `conn = client.connections.create(ConnectionCreate(name="azure", type="http_basic", extension="@cognigy/basic-nodes", fields={"username":"u"}, project_id="507f…"))` |
| `get(connection_id)`                                                  | Get Connection by ID                         | `conn = client.connections.get("507f…")`                                                                      |
| `update(connection_id, data)`                                         | Update Connection fields                     | `client.connections.update("507f…", ConnectionUpdate(fields={"username":"x"}))`                               |
| `delete(connection_id)`                                               | Delete a Connection                          | `client.connections.delete("507f…")`                                                                          |
| `batch(operations, project_id?)`                                      | Batch create/update/delete Connections       | `result = client.connections.batch([ConnectionBatchDeleteOp(id="507f…")])`                                    |
| `create_field(connection_id, key=, value=)`                           | Add a key/value field to a Connection        | `client.connections.create_field("507f…", key="region", value="eu")`                                          |
| `delete_field(connection_id, field_name)`                             | Remove a field from a Connection             | `client.connections.delete_field("507f…", "region")`                                                          |
| `list_schemas(project_id?, filter?, limit?, sort?, cursors?)`         | List available Connection schemas            | `schemas = client.connections.list_schemas(project_id="507f…")`                                               |

**Example:**

```python
from cognigy import (
    CognigyClient,
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionBatchCreateOp,
    ConnectionBatchCreateValue,
    ConnectionBatchDeleteOp,
    ResourceLevel,
)

with CognigyClient(api_key="your-api-key") as client:
    conns = client.connections.list(project_id="507f1f77bcf86cd799439011")

    conn = client.connections.create(ConnectionCreate(
        name="azure-openai",
        type="api-key",
        extension="@cognigy/basic-nodes",
        fields={"apiKey": "x123"},
        project_id="507f1f77bcf86cd799439011",
    ))

    client.connections.update(conn.id, ConnectionUpdate(fields={"apiKey": "y456"}))

    client.connections.create_field(conn.id, key="region", value="eu")

    result = client.connections.batch([
        ConnectionBatchCreateOp(value=ConnectionBatchCreateValue(
            name="extra",
            type="api-key",
            extension="@cognigy/basic-nodes",
            fields={"apiKey": "z789"},
        )),
        ConnectionBatchDeleteOp(id=conn.id),
    ], project_id="507f1f77bcf86cd799439011")
    print(result.created, result.deleted)

    schemas = client.connections.list_schemas()
```

---

## License

This project is licensed under the [MIT License](LICENSE).

**Trademark notice:** Cognigy®, Cognigy.AI®, and related marks are trademarks of Cognigy GmbH. This project is not affiliated with, endorsed by, or supported by Cognigy GmbH.
