import re

from backend.app.ingestion.access_parser import AccessLogParser
from backend.app.ingestion.json_parser import JsonLogParser
from backend.app.ingestion.parser_models import (
    ParseResult,
    ParseStatus,
    ParsedLogLine,
)


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<message>.*)$"
)

HTTP_PATTERN = re.compile(
    r"^(?P<method>GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+"
    r"(?P<endpoint>\S+)\s+"
    r"(?P<status_code>\d{3})\s+"
    r"(?P<response_time>\d+(?:\.\d+)?)ms$"
)

TRACE_ID_PATTERN = re.compile(
    r"(?:trace_id|traceId)=([A-Za-z0-9._:-]+)"
)

HOST_PATTERN = re.compile(
    r"(?:host)=([A-Za-z0-9._:-]+)"
)


class StandardLogParser:
    """Parse the standard application log format."""

    def parse(self, line: str) -> ParseResult:
        match = LOG_PATTERN.match(line)

        if not match:
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Line does not match the standard log format.",
            )

        try:
            timestamp = self._parse_timestamp(match.group("timestamp"))
            level = match.group("level")
            message = match.group("message")

            endpoint = None
            method = None
            status_code = None
            response_time = None

            http_match = HTTP_PATTERN.match(message)

            if http_match:
                method = http_match.group("method")
                endpoint = http_match.group("endpoint")
                status_code = int(http_match.group("status_code"))
                response_time = float(http_match.group("response_time"))

            trace_match = TRACE_ID_PATTERN.search(message)
            trace_id = trace_match.group(1) if trace_match else None

            host_match = HOST_PATTERN.search(message)
            host = host_match.group(1) if host_match else None

            parsed_log = ParsedLogLine(
                timestamp=timestamp,
                level=level,
                message=message,
                service=None,
                host=host,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                exception=None,
                trace_id=trace_id,
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
    def _parse_timestamp(value: str):
        from datetime import datetime

        return datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S",
        )


class LogParser:
    """Entry point for supported log parsers."""

    def __init__(self) -> None:
        self.standard_parser = StandardLogParser()
        self.json_parser = JsonLogParser()
        self.access_parser = AccessLogParser()

    def parse(self, line: str) -> ParsedLogLine | None:
        """Backward-compatible parser interface."""

        result = self.parse_with_result(line)

        if result.status == ParseStatus.PARSED:
            return result.parsed_log

        return None

    def parse_with_result(self, line: str) -> ParseResult:
        """Detect the log format and return the full parsing result."""

        stripped_line = line.strip()

        if not stripped_line:
            return ParseResult(
                status=ParseStatus.UNKNOWN_FORMAT,
                error_message="Empty log line.",
            )

        # JSON logs
        if stripped_line.startswith("{"):
            return self.json_parser.parse(stripped_line)

        # Apache/Nginx-style access logs
        if self._looks_like_access_log(stripped_line):
            return self.access_parser.parse(stripped_line)

        # Standard application logs
        if self._looks_like_standard_log(stripped_line):
            return self.standard_parser.parse(stripped_line)

        return ParseResult(
            status=ParseStatus.UNKNOWN_FORMAT,
            error_message="Unable to detect log format.",
        )

    @staticmethod
    def _looks_like_access_log(line: str) -> bool:
        """Return True when the line resembles an access log."""

        return bool(
            re.match(
                r"^\S+\s+\S+\s+\S+\s+\[[^\]]+\]\s+\"",
                line,
            )
        )

    @staticmethod
    def _looks_like_standard_log(line: str) -> bool:
        """Return True when the line resembles a standard application log."""

        return bool(
            re.match(
                r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[A-Z]+",
                line,
            )
        )