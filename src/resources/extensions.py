"""
Extensions resource for the Cognigy API (v2.0 /extensions).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, List, Optional, Union, overload

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient

from ..exceptions import CognigyValidationError
from ..models.extension import (
    Extension,
    ExtensionBackgroundTask,
    ExtensionListItem,
    ExtensionSettingsUpdate,
    ExtensionUpdatePackageByUrl,
    ExtensionUploadByUrl,
)
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data

OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")


def _require_object_id(value: str, field_name: str) -> None:
    if not OBJECT_ID_PATTERN.match(value):
        raise CognigyValidationError(
            f"{field_name} must be a 24-character lowercase hex ObjectId, got {value!r}."
        )


class ExtensionsResource:
    """Synchronous resource for Cognigy Extensions."""

    def __init__(self, client: CognigyClient) -> None:
        self._client = client

    def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ExtensionListItem]:
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={**({"projectId": project_id} if project_id else {})},
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/extensions", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [ExtensionListItem(**item) for item in items]

    def get(self, extension_id: str, **kwargs: Any) -> Extension:
        _require_object_id(extension_id, "extension_id")
        data = self._client._request(
            "GET", f"/v2.0/extensions/{extension_id}", **kwargs
        )
        return Extension(**data)

    def delete(self, extension_id: str, **kwargs: Any) -> None:
        _require_object_id(extension_id, "extension_id")
        self._client._request("DELETE", f"/v2.0/extensions/{extension_id}", **kwargs)

    def update_settings(
        self, extension_id: str, data: ExtensionSettingsUpdate, **kwargs: Any
    ) -> None:
        _require_object_id(extension_id, "extension_id")
        data = validate_create_update_data(data, ExtensionSettingsUpdate)
        self._client._request(
            "PATCH", f"/v2.0/extensions/{extension_id}", data=data, **kwargs
        )

    def upload(self, data: ExtensionUploadByUrl, **kwargs: Any) -> ExtensionBackgroundTask:
        data = validate_create_update_data(data, ExtensionUploadByUrl)
        response = self._client._request(
            "POST", "/v2.0/extensions/upload", data=data, **kwargs
        )
        return ExtensionBackgroundTask(**response)

    def create(
        self,
        project_id: str,
        file: Union[str, Path, BinaryIO, bytes, bytearray],
        *,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask:
        _require_object_id(project_id, "project_id")
        files, form_data = _prepare_extension_file_upload(
            project_id=project_id, extension=None, file=file, filename=filename
        )
        response = self._client._request(
            "POST",
            "/v2.0/extensions/upload",
            data=form_data,
            files=files,
            **kwargs,
        )
        return ExtensionBackgroundTask(**response)

    @overload
    def update(
        self, data: ExtensionUpdatePackageByUrl, **kwargs: Any
    ) -> ExtensionBackgroundTask: ...

    @overload
    def update(
        self,
        *,
        project_id: str,
        extension: str,
        file: Union[str, Path, BinaryIO, bytes, bytearray],
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask: ...

    def update(
        self,
        data: Optional[ExtensionUpdatePackageByUrl] = None,
        *,
        project_id: Optional[str] = None,
        extension: Optional[str] = None,
        file: Optional[Union[str, Path, BinaryIO, bytes, bytearray]] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask:
        """POST ``/v2.0/extensions/update`` — JSON body or multipart file."""
        if data is not None:
            if project_id is not None or extension is not None or file is not None:
                raise CognigyValidationError(
                    "Use either ``data=`` (JSON) or keyword multipart arguments, not both."
                )
            data = validate_create_update_data(data, ExtensionUpdatePackageByUrl)
            response = self._client._request(
                "POST", "/v2.0/extensions/update", data=data, **kwargs
            )
            return ExtensionBackgroundTask(**response)

        if file is None:
            raise CognigyValidationError(
                "Provide ``data`` (ExtensionUpdatePackageByUrl) or "
                "``project_id``, ``extension``, and ``file`` for multipart."
            )
        if not project_id or not extension:
            raise CognigyValidationError(
                "Multipart update requires ``project_id`` and ``extension``."
            )
        _require_object_id(project_id, "project_id")
        files, form_data = _prepare_extension_file_upload(
            project_id=project_id, extension=extension, file=file, filename=filename
        )
        response = self._client._request(
            "POST",
            "/v2.0/extensions/update",
            data=form_data,
            files=files,
            **kwargs,
        )
        return ExtensionBackgroundTask(**response)


class AsyncExtensionsResource:
    """Asynchronous resource for Cognigy Extensions."""

    def __init__(self, client: AsyncCognigyClient) -> None:
        self._client = client

    async def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ExtensionListItem]:
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={**({"projectId": project_id} if project_id else {})},
        )

        async def make_request(p):
            return await self._client._request(
                "GET", "/v2.0/extensions", params=p, **kwargs
            )

        items = await paginate_async(make_request, params, user_limit=limit)
        return [ExtensionListItem(**item) for item in items]

    async def get(self, extension_id: str, **kwargs: Any) -> Extension:
        _require_object_id(extension_id, "extension_id")
        data = await self._client._request(
            "GET", f"/v2.0/extensions/{extension_id}", **kwargs
        )
        return Extension(**data)

    async def delete(self, extension_id: str, **kwargs: Any) -> None:
        _require_object_id(extension_id, "extension_id")
        await self._client._request(
            "DELETE", f"/v2.0/extensions/{extension_id}", **kwargs
        )

    async def update_settings(
        self, extension_id: str, data: ExtensionSettingsUpdate, **kwargs: Any
    ) -> None:
        _require_object_id(extension_id, "extension_id")
        data = validate_create_update_data(data, ExtensionSettingsUpdate)
        await self._client._request(
            "PATCH", f"/v2.0/extensions/{extension_id}", data=data, **kwargs
        )

    async def upload(
        self, data: ExtensionUploadByUrl, **kwargs: Any
    ) -> ExtensionBackgroundTask:
        data = validate_create_update_data(data, ExtensionUploadByUrl)
        response = await self._client._request(
            "POST", "/v2.0/extensions/upload", data=data, **kwargs
        )
        return ExtensionBackgroundTask(**response)

    async def create(
        self,
        project_id: str,
        file: Union[str, Path, BinaryIO, bytes, bytearray],
        *,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask:
        _require_object_id(project_id, "project_id")
        files, form_data = _prepare_extension_file_upload(
            project_id=project_id, extension=None, file=file, filename=filename
        )
        response = await self._client._request(
            "POST",
            "/v2.0/extensions/upload",
            data=form_data,
            files=files,
            **kwargs,
        )
        return ExtensionBackgroundTask(**response)

    @overload
    async def update(
        self, data: ExtensionUpdatePackageByUrl, **kwargs: Any
    ) -> ExtensionBackgroundTask: ...

    @overload
    async def update(
        self,
        *,
        project_id: str,
        extension: str,
        file: Union[str, Path, BinaryIO, bytes, bytearray],
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask: ...

    async def update(
        self,
        data: Optional[ExtensionUpdatePackageByUrl] = None,
        *,
        project_id: Optional[str] = None,
        extension: Optional[str] = None,
        file: Optional[Union[str, Path, BinaryIO, bytes, bytearray]] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ExtensionBackgroundTask:
        """POST ``/v2.0/extensions/update`` — JSON body or multipart file."""
        if data is not None:
            if project_id is not None or extension is not None or file is not None:
                raise CognigyValidationError(
                    "Use either ``data=`` (JSON) or keyword multipart arguments, not both."
                )
            data = validate_create_update_data(data, ExtensionUpdatePackageByUrl)
            response = await self._client._request(
                "POST", "/v2.0/extensions/update", data=data, **kwargs
            )
            return ExtensionBackgroundTask(**response)

        if file is None:
            raise CognigyValidationError(
                "Provide ``data`` (ExtensionUpdatePackageByUrl) or "
                "``project_id``, ``extension``, and ``file`` for multipart."
            )
        if not project_id or not extension:
            raise CognigyValidationError(
                "Multipart update requires ``project_id`` and ``extension``."
            )
        _require_object_id(project_id, "project_id")
        files, form_data = _prepare_extension_file_upload(
            project_id=project_id, extension=extension, file=file, filename=filename
        )
        response = await self._client._request(
            "POST",
            "/v2.0/extensions/update",
            data=form_data,
            files=files,
            **kwargs,
        )
        return ExtensionBackgroundTask(**response)


def _prepare_extension_file_upload(
    *,
    project_id: str,
    extension: Optional[str],
    file: Union[str, Path, BinaryIO, bytes, bytearray],
    filename: Optional[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build httpx ``files`` and form ``data`` for multipart upload/update."""
    if isinstance(file, (str, Path)):
        path = Path(file)
        body = path.read_bytes()
        fname = filename or path.name
    elif isinstance(file, (bytes, bytearray)):
        body = bytes(file)
        if not filename:
            raise CognigyValidationError(
                "filename is required when passing raw bytes for the extension file."
            )
        fname = filename
    else:
        body = file.read()
        if not filename:
            raise CognigyValidationError(
                "filename is required when passing a binary stream for the extension file."
            )
        fname = filename

    files = {"file": (fname, body, "application/gzip")}
    form_data: dict[str, Any] = {"projectId": project_id}
    if extension is not None:
        form_data["extension"] = extension
    return files, form_data
