import logging
import os
import httpx
from typing import Optional
from .exceptions import CognigyConfigurationError, CognigyAPIError

logger = logging.getLogger(__name__)

class AsyncCognigyClient:
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
        if "api-" not in self._base_url.lower():
            raise CognigyConfigurationError(
                "Invalid base URL. Base URL must contain 'api-' in the domain name."
                "Example: 'https://api-app.cognigy.ai' if you use the 'app.cognigy.ai' domain."
            )

        self.http_client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "X-API-Key": self._api_key,
                "Accept": "application/json",
            },
            timeout=timeout
        )

        # Initialize resources
        from .resources.projects import AsyncProjectsResource
        from .resources.flows import AsyncFlowsResource
        from .resources.nodes import AsyncNodesResource
        from .resources.aiagents import AsyncAIAgentsResource
        from .resources.analytics import AsyncAnalyticsResource
        from .resources.conversations import AsyncConversationsResource
        from .resources.knowledge_stores import AsyncKnowledgeStoresResource
        from .resources.knowledge_chunks import AsyncKnowledgeChunksResource
        from .resources.knowledge_sources import AsyncKnowledgeSourcesResource
        from .resources.knowledge_connectors import AsyncKnowledgeConnectorsResource
        from .resources.locales import AsyncLocalesResource
        from .resources.logs import AsyncLogsResource
        from .resources.tasks import AsyncTasksResource
        from .resources.search import AsyncSearchResource
        from .resources.snapshots import AsyncSnapshotsResource
        from .resources.extensions import AsyncExtensionsResource
        from .resources.functions import AsyncFunctionsResource
        from .resources.llm import AsyncLLMResource
        from .resources.connections import AsyncConnectionsResource

        self.projects: AsyncProjectsResource = AsyncProjectsResource(self)
        self.flows: AsyncFlowsResource = AsyncFlowsResource(self)
        self.nodes: AsyncNodesResource = AsyncNodesResource(self)
        self.aiagents: AsyncAIAgentsResource = AsyncAIAgentsResource(self)
        self.analytics: AsyncAnalyticsResource = AsyncAnalyticsResource(self)
        self.conversations: AsyncConversationsResource = AsyncConversationsResource(self)
        self.knowledge_stores: AsyncKnowledgeStoresResource = AsyncKnowledgeStoresResource(self)
        self.knowledge_chunks: AsyncKnowledgeChunksResource = AsyncKnowledgeChunksResource(self)
        self.knowledge_sources: AsyncKnowledgeSourcesResource = AsyncKnowledgeSourcesResource(self)
        self.knowledge_connectors: AsyncKnowledgeConnectorsResource = AsyncKnowledgeConnectorsResource(self)
        self.locales: AsyncLocalesResource = AsyncLocalesResource(self)
        self.logs: AsyncLogsResource = AsyncLogsResource(self)
        self.tasks: AsyncTasksResource = AsyncTasksResource(self)
        self.search: AsyncSearchResource = AsyncSearchResource(self)
        self.snapshots: AsyncSnapshotsResource = AsyncSnapshotsResource(self)
        self.extensions: AsyncExtensionsResource = AsyncExtensionsResource(self)
        self.functions: AsyncFunctionsResource = AsyncFunctionsResource(self)
        self.llm: AsyncLLMResource = AsyncLLMResource(self)
        self.connections: AsyncConnectionsResource = AsyncConnectionsResource(self)

    async def close(self):
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(self, method: str, path: str, **kwargs):
        # Serialize Pydantic model if passed as data parameter (JSON body).
        # When ``files`` is set, ``data`` is left as multipart form fields.
        if "data" in kwargs and "files" not in kwargs:
            data = kwargs.pop("data")
            if hasattr(data, "model_dump"):
                kwargs["json"] = data.model_dump(by_alias=True, exclude_none=True)
            else:
                kwargs["json"] = data

        response = await self.http_client.request(method, path, **kwargs)
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
