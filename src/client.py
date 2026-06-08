import logging
import os
import httpx
from typing import Optional
from .exceptions import CognigyConfigurationError, CognigyAPIError

logger = logging.getLogger(__name__)

class CognigyClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60
    ):
        self._api_key = api_key or os.getenv("COGNIGY_API_KEY")
        if not self._api_key:
            raise CognigyConfigurationError(
                "API Key is required. Provide it as an argument or set COGNIGY_API_KEY environment variable."
            )

        self._base_url = base_url or os.getenv("COGNIGY_BASE_URL", "https://api-app.cognigy.ai")
        if "api-" not in self._base_url.lower() and "api.live.ai.telekomcloud.com" not in self._base_url.lower():
            raise CognigyConfigurationError(
                "Invalid base URL. Base URL must contain 'api-' in the domain name."
                "Example: 'https://api-app.cognigy.ai' if you use the 'app.cognigy.ai' domain."
            )
        
        self.http_client: httpx.Client = httpx.Client(
            base_url=self._base_url,
            headers={
                "X-API-Key": self._api_key,
                "Accept": "application/json",
            },
            timeout=timeout
        )

        # Initialize resources
        from .resources.projects import ProjectsResource
        from .resources.flows import FlowsResource
        from .resources.nodes import NodesResource
        from .resources.aiagents import AIAgentsResource
        from .resources.analytics import AnalyticsResource
        from .resources.conversations import ConversationsResource
        from .resources.knowledge_stores import KnowledgeStoresResource
        from .resources.knowledge_chunks import KnowledgeChunksResource
        from .resources.knowledge_sources import KnowledgeSourcesResource
        from .resources.knowledge_connectors import KnowledgeConnectorsResource
        from .resources.locales import LocalesResource
        from .resources.logs import LogsResource
        from .resources.tasks import TasksResource
        from .resources.search import SearchResource
        from .resources.snapshots import SnapshotsResource
        from .resources.extensions import ExtensionsResource
        from .resources.functions import FunctionsResource
        from .resources.llm import LLMResource
        from .resources.connections import ConnectionsResource

        self.projects: ProjectsResource = ProjectsResource(self)
        self.flows: FlowsResource = FlowsResource(self)
        self.nodes: NodesResource = NodesResource(self)
        self.aiagents: AIAgentsResource = AIAgentsResource(self)
        self.analytics: AnalyticsResource = AnalyticsResource(self)
        self.conversations: ConversationsResource = ConversationsResource(self)
        self.knowledge_stores: KnowledgeStoresResource = KnowledgeStoresResource(self)
        self.knowledge_chunks: KnowledgeChunksResource = KnowledgeChunksResource(self)
        self.knowledge_sources: KnowledgeSourcesResource = KnowledgeSourcesResource(self)
        self.knowledge_connectors: KnowledgeConnectorsResource = KnowledgeConnectorsResource(self)
        self.locales: LocalesResource = LocalesResource(self)
        self.logs: LogsResource = LogsResource(self)
        self.tasks: TasksResource = TasksResource(self)
        self.search: SearchResource = SearchResource(self)
        self.snapshots: SnapshotsResource = SnapshotsResource(self)
        self.extensions: ExtensionsResource = ExtensionsResource(self)
        self.functions: FunctionsResource = FunctionsResource(self)
        self.llm: LLMResource = LLMResource(self)
        self.connections: ConnectionsResource = ConnectionsResource(self)

    def close(self):
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _request(self, method: str, path: str, **kwargs):
        # Serialize Pydantic model if passed as data parameter (JSON body).
        # When ``files`` is set, ``data`` is left as multipart form fields.
        if "data" in kwargs and "files" not in kwargs:
            data = kwargs.pop("data")
            if hasattr(data, "model_dump"):
                kwargs["json"] = data.model_dump(by_alias=True, exclude_none=True)
            else:
                kwargs["json"] = data

        response = self.http_client.request(method, path, **kwargs)
        if not response.is_success:
            logger.debug("API error response: %s", response.text)
            try:
                response_body = response.json()
            except Exception:
                response_body = response.text or None
            raise CognigyAPIError(
                message=f"API request failed: {response.reason_phrase}",
                status_code=response.status_code,
                response_body=response_body
            )
        # Cognigy update endpoints may return 204 No Content or empty body
        if response.status_code == 204 or not response.text.strip():
            return None
        try:
            return response.json()
        except Exception:
            logger.debug("Failed to parse JSON response: %s", response.text)
            raise
