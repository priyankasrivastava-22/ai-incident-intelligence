from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ParseStatus(str, Enum):
    """Represent the outcome of parsing a log line."""

    PARSED = "parsed"
    MALFORMED = "malformed"
    UNKNOWN_FORMAT = "unknown_format"
    PARSER_ERROR = "parser_error"


@dataclass
class ParsedLogLine:
    """Structured representation of a parsed log line."""

    timestamp: datetime
    level: str
    message: str
    service: str | None = None
    host: str | None = None
    endpoint: str | None = None
    method: str | None = None
    status_code: int | None = None
    response_time: float | None = None
    exception: str | None = None
    trace_id: str | None = None
    client_ip: str | None = None
    http_version: str | None = None
    response_size: int | None = None


@dataclass
class ParseResult:
    """Represent the result of parsing a single log line."""

    status: ParseStatus
    parsed_log: ParsedLogLine | None = None
    error_message: str | None = None


@dataclass
class ParsingStatistics:
    """Track parsing results across multiple log lines."""

    total_lines: int = 0
    parsed_lines: int = 0
    skipped_lines: int = 0
    malformed_lines: int = 0
    unknown_format_lines: int = 0
    parser_errors: int = 0

    def record(self, result: ParseResult) -> None:
        """Update statistics using a single parse result."""

        self.total_lines += 1

        if result.status == ParseStatus.PARSED:
            self.parsed_lines += 1

        elif result.status == ParseStatus.MALFORMED:
            self.malformed_lines += 1
            self.skipped_lines += 1

        elif result.status == ParseStatus.UNKNOWN_FORMAT:
            self.unknown_format_lines += 1
            self.skipped_lines += 1

        elif result.status == ParseStatus.PARSER_ERROR:
            self.parser_errors += 1
            self.skipped_lines += 1