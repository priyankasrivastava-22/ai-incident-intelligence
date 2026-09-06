import re
from datetime import datetime
from typing import Any

from backend.app.ingestion.parser_models import (
    ParseResult,
    ParseStatus,
    ParsedLogLine,
)


ACCESS_LOG_PATTERN = re.compile(
    r'^(?P<client_ip>\S+)\s+'
    r'\S+\s+'
    r'\S+\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+'
    r'(?P<endpoint>\S+)\s+'
    r'(?P<http_version>HTTP/\d(?:\.\d)?)"\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<size>\d+|-)$'
)


class AccessLogParser:
    """Parse Apache/Nginx-style access log lines."""

    def parse(self, line: str) -> ParseResult:
        """Parse a single access log line."""

        line = line.strip()

        if not line:
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Empty log line.",
            )

        match = ACCESS_LOG_PATTERN.match(line)

        if not match:
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Line does not match the access log format.",
            )

        try:
            timestamp = datetime.strptime(
                match.group("timestamp"),
                "%d/%b/%Y:%H:%M:%S %z",
            )

            client_ip = match.group("client_ip")
            method = match.group("method")
            endpoint = match.group("endpoint")
            http_version = match.group("http_version")
            status_code = int(match.group("status"))
            response_size = (
                None
                if match.group("size") == "-"
                else int(match.group("size"))
            )

            parsed_log = ParsedLogLine(
                timestamp=timestamp,
                level=self._level_from_status(status_code),
                message=(
                    f"{method} {endpoint} "
                    f"{status_code} {http_version}"
                ),
                host=None,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=None,
                exception=None,
                trace_id=None,
                service=None,
                client_ip=client_ip,
                http_version=http_version,
                response_size=response_size,
            )

            return ParseResult(
                status=ParseStatus.PARSED,
                parsed_log=parsed_log,
            )

        except (TypeError, ValueError, OverflowError) as exc:
            return ParseResult(
                status=ParseStatus.PARSER_ERROR,
                error_message=str(exc),
            )

    @staticmethod
    def _level_from_status(status_code: int) -> str:
        """Map HTTP status codes to a log severity."""

        if status_code >= 500:
            return "ERROR"

        if status_code >= 400:
            return "WARNING"

        return "INFO"