import json
from datetime import datetime
from typing import Any

from backend.app.ingestion.parser_models import (
    ParseResult,
    ParseStatus,
    ParsedLogLine,
)


class JsonLogParser:
    """Parse JSON-formatted application log lines."""

    REQUIRED_FIELDS = {
        "timestamp",
        "level",
        "message",
    }

    def parse(self, line: str) -> ParseResult:
        """Parse a single JSON log line."""

        line = line.strip()

        if not line:
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Empty log line.",
            )

        if not line.startswith("{"):
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Line does not appear to be JSON.",
            )

        try:
            data: Any = json.loads(line)

        except json.JSONDecodeError as exc:
            return ParseResult(
                status=ParseStatus.MALFORMED,
                error_message=f"Invalid JSON: {exc.msg}",
            )

        if not isinstance(data, dict):
            return ParseResult(
                status=ParseStatus.MALFORMED,
                error_message="JSON log must be a JSON object.",
            )

        missing_fields = self.REQUIRED_FIELDS - data.keys()

        if missing_fields:
            return ParseResult(
                status=ParseStatus.MALFORMED,
                error_message=(
                    "Missing required fields: "
                    + ", ".join(sorted(missing_fields))
                ),
            )

        try:
            timestamp = self._parse_timestamp(data["timestamp"])

            level = self._require_string(
                data["level"],
                "level",
            )

            message = self._require_string(
                data["message"],
                "message",
            )

            service = self._optional_string(
                data.get("service"),
                "service",
            )

            host = self._optional_string(
                data.get("host"),
                "host",
            )

            endpoint = self._optional_string(
                data.get("endpoint"),
                "endpoint",
            )

            method = self._optional_string(
                data.get("method"),
                "method",
            )

            trace_id = self._optional_string(
                data.get("trace_id", data.get("traceId")),
                "trace_id",
            )

            exception = self._optional_string(
                data.get("exception"),
                "exception",
            )

            status_code = self._optional_int(
                data.get("status_code", data.get("statusCode")),
                "status_code",
            )

            response_time = self._optional_float(
                data.get(
                    "response_time",
                    data.get("responseTime"),
                ),
                "response_time",
            )

            parsed_log = ParsedLogLine(
                timestamp=timestamp,
                level=level,
                message=message,
                host=host,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                exception=exception,
                trace_id=trace_id,
            )

            return ParseResult(
                status=ParseStatus.PARSED,
                parsed_log=parsed_log,
            )

        except (TypeError, ValueError) as exc:
            return ParseResult(
                status=ParseStatus.MALFORMED,
                error_message=str(exc),
            )

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        """Parse an ISO-8601 timestamp."""

        if not isinstance(value, str):
            raise ValueError(
                "Field 'timestamp' must be a string."
            )

        normalized_value = value.strip()

        if normalized_value.endswith("Z"):
            normalized_value = normalized_value[:-1] + "+00:00"

        try:
            return datetime.fromisoformat(normalized_value)

        except ValueError as exc:
            raise ValueError(
                "Field 'timestamp' must contain a valid ISO-8601 timestamp."
            ) from exc

    @staticmethod
    def _require_string(
        value: Any,
        field_name: str,
    ) -> str:
        """Validate a required string field."""

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Field '{field_name}' must be a non-empty string."
            )

        return value.strip()

    @staticmethod
    def _optional_string(
        value: Any,
        field_name: str,
    ) -> str | None:
        """Validate an optional string field."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                f"Field '{field_name}' must be a string."
            )

        return value.strip() or None

    @staticmethod
    def _optional_int(
        value: Any,
        field_name: str,
    ) -> int | None:
        """Validate an optional integer field."""

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"Field '{field_name}' must be an integer."
            )

        return value

    @staticmethod
    def _optional_float(
        value: Any,
        field_name: str,
    ) -> float | None:
        """Validate an optional numeric field."""

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ValueError(
                f"Field '{field_name}' must be a number."
            )

        return float(value)