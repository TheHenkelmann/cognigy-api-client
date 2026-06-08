"""
LLM resource for the Cognigy API (v2.0 ``/largelanguagemodels``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Union

from pydantic import ValidationError

from ..exceptions import CognigyValidationError
from ..models.llm import (
    LLM,
    LLMCreateForOrganisation,
    LLMCreateForProject,
    LLMTestResult,
    LLMUpdate,
)
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient


def _coerce_llm_create(
    data: Union[LLMCreateForProject, LLMCreateForOrganisation, Any],
) -> Union[LLMCreateForProject, LLMCreateForOrganisation]:
    if isinstance(data, (LLMCreateForProject, LLMCreateForOrganisation)):
        return data
    raw = data.model_dump(by_alias=True) if hasattr(data, "model_dump") else dict(data)
    try:
        if raw.get("resourceLevel") == "organisation":
            return LLMCreateForOrganisation.model_validate(raw)
        return LLMCreateForProject.model_validate(raw)
    except ValidationError as e:
        raise CognigyValidationError(
            "Data does not match project or organisation LLM create schema.",
            errors=e.errors(),
        ) from e


class LLMResource:
    """Synchronous CRUD + connection test for LLMs."""

    def __init__(self, client: CognigyClient) -> None:
        self._client = client

    def list(
        self,
        project_id: Optional[str] = None,
        resource_level: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LLM]:
        extra: dict[str, Any] = {}
        if project_id is not None:
            extra["projectId"] = project_id
        if resource_level is not None:
            extra["resourceLevel"] = resource_level

        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra=extra or None,
        )

        def make_request(p: dict[str, Any]) -> dict[str, Any]:
            return self._client._request("GET", "/v2.0/largelanguagemodels", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [LLM(**item) for item in items]

    def create(
        self,
        data: Union[LLMCreateForProject, LLMCreateForOrganisation, Any],
        **kwargs: Any,
    ) -> LLM:
        payload = _coerce_llm_create(data)
        response = self._client._request(
            "POST", "/v2.0/largelanguagemodels", data=payload, **kwargs
        )
        return LLM(**response)

    def get(self, llm_id: str, **kwargs: Any) -> LLM:
        data = self._client._request(
            "GET",
            f"/v2.0/largelanguagemodels/{llm_id}",
            **kwargs,
        )
        return LLM(**data)

    def update(
        self,
        llm_id: str,
        data: LLMUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[LLM]:
        validated = validate_create_update_data(data, LLMUpdate)
        response = self._client._request(
            "PATCH",
            f"/v2.0/largelanguagemodels/{llm_id}",
            data=validated,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return self.get(llm_id, **kwargs)
            return None
        return LLM(**response)

    def delete(
        self,
        llm_id: str,
        *,
        force: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        params = {}
        if force is not None:
            params["force"] = "true" if force else "false"
        self._client._request(
            "DELETE",
            f"/v2.0/largelanguagemodels/{llm_id}",
            params=params or None,
            **kwargs,
        )

    def test(self, llm_id: str, **kwargs: Any) -> LLMTestResult:
        """Test provider credentials; only ``llm_id`` is sent (no JSON body)."""
        raw = self._client._request(
            "POST",
            f"/v2.0/largelanguagemodels/{llm_id}/test",
            **kwargs,
        )
        return LLMTestResult.model_validate(raw)


class AsyncLLMResource:
    """Asynchronous CRUD + connection test for LLMs."""

    def __init__(self, client: AsyncCognigyClient) -> None:
        self._client = client

    async def list(
        self,
        project_id: Optional[str] = None,
        resource_level: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LLM]:
        extra: dict[str, Any] = {}
        if project_id is not None:
            extra["projectId"] = project_id
        if resource_level is not None:
            extra["resourceLevel"] = resource_level

        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra=extra or None,
        )

        async def make_request(p: dict[str, Any]) -> dict[str, Any]:
            return await self._client._request(
                "GET", "/v2.0/largelanguagemodels", params=p, **kwargs
            )

        items = await paginate_async(make_request, params, user_limit=limit)
        return [LLM(**item) for item in items]

    async def create(
        self,
        data: Union[LLMCreateForProject, LLMCreateForOrganisation, Any],
        **kwargs: Any,
    ) -> LLM:
        payload = _coerce_llm_create(data)
        response = await self._client._request(
            "POST", "/v2.0/largelanguagemodels", data=payload, **kwargs
        )
        return LLM(**response)

    async def get(self, llm_id: str, **kwargs: Any) -> LLM:
        data = await self._client._request(
            "GET",
            f"/v2.0/largelanguagemodels/{llm_id}",
            **kwargs,
        )
        return LLM(**data)

    async def update(
        self,
        llm_id: str,
        data: LLMUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[LLM]:
        validated = validate_create_update_data(data, LLMUpdate)
        response = await self._client._request(
            "PATCH",
            f"/v2.0/largelanguagemodels/{llm_id}",
            data=validated,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return await self.get(llm_id, **kwargs)
            return None
        return LLM(**response)

    async def delete(
        self,
        llm_id: str,
        *,
        force: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        params = {}
        if force is not None:
            params["force"] = "true" if force else "false"
        await self._client._request(
            "DELETE",
            f"/v2.0/largelanguagemodels/{llm_id}",
            params=params or None,
            **kwargs,
        )

    async def test(self, llm_id: str, **kwargs: Any) -> LLMTestResult:
        """Test provider credentials; only ``llm_id`` is sent (no JSON body)."""
        raw = await self._client._request(
            "POST",
            f"/v2.0/largelanguagemodels/{llm_id}/test",
            **kwargs,
        )
        return LLMTestResult.model_validate(raw)
