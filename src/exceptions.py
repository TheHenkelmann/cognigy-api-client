class CognigyError(Exception):
    """Base exception for all Cognigy SDK errors."""
    pass


class CognigyConfigurationError(CognigyError):
    """Raised when the client is not configured correctly (e.g. missing API key)."""
    pass


class CognigyAPIError(CognigyError):
    """Raised when the Cognigy API returns an error response."""
    def __init__(self, message: str, status_code: int, response_body=None):
        detail = ""
        if response_body and isinstance(response_body, dict) and response_body.get("detail"):
            detail = f" - {response_body.get('detail')}"
        super().__init__(f"(Status: {status_code}) {message}{detail}")
        self.status_code = status_code
        self.response_body = response_body


class CognigyValidationError(CognigyError):
    """Raised when create/update data fails validation against the expected Pydantic model."""
    def __init__(self, message: str, errors: list = None):
        super().__init__(message)
        self.errors = errors or []

    def __str__(self) -> str:
        if not self.errors:
            return self.args[0] if self.args else "Validation failed."
        lines = [self.args[0] if self.args else "Validation failed:"]
        for err in self.errors:
            loc = " -> ".join(str(x) for x in err.get("loc", ()))
            msg = err.get("msg", "")
            ctx = err.get("ctx")
            if ctx:
                msg = f"{msg} (context: {ctx})"
            lines.append(f"  • {loc}: {msg}")
        return "\n".join(lines)
