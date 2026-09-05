import re
from dataclasses import dataclass
from datetime import datetime


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


@dataclass
class ParsedLogLine:
    """Structured representation of a parsed log line."""

    timestamp: datetime
    level: str
    message: str
    host: str | None = None
    endpoint: str | None = None
    method: str | None = None
    status_code: int | None = None
    response_time: float | None = None
    exception: str | None = None
    trace_id: str | None = None


class LogParser:
    """Parse supported application log formats."""

    def parse(self, line: str) -> ParsedLogLine | None:
        """Parse a single log line.

        Returns None when the line does not match the supported
        timestamp + log-level format.
        """

        line = line.strip()

        if not line:
            return None

        match = LOG_PATTERN.match(line)

        if not match:
            return None

        timestamp = datetime.strptime(
            match.group("timestamp"),
            "%Y-%m-%d %H:%M:%S",
        )

        level = match.group("level")
        message = match.group("message").strip()

        method = None
        endpoint = None
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

        exception = None

        if level in {"ERROR", "CRITICAL", "FATAL"}:
            exception = message

        return ParsedLogLine(
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