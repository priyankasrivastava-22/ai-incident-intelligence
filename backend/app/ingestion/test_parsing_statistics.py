from backend.app.ingestion.parser import LogParser
from backend.app.ingestion.parser_models import (
    ParseStatus,
    ParsingStatistics,
)


def test_parsing_statistics() -> None:
    parser = LogParser()
    statistics = ParsingStatistics()

    lines = [
        "2026-09-04 10:00:01 INFO Booking service started",
        (
            "2026-09-04 10:00:02 ERROR "
            "Database connection failed trace_id=abc123"
        ),
        (
            '{"timestamp":"2026-09-04T10:00:03Z",'
            '"level":"ERROR",'
            '"service":"booking-api",'
            '"message":"Database timeout"}'
        ),
        (
            '192.168.1.10 - - '
            '[04/Sep/2026:10:00:04 +0000] '
            '"GET /api/bookings HTTP/1.1" 500 1245'
        ),
        "this is not a supported log format",
    ]

    for line in lines:
        result = parser.parse_with_result(line)
        statistics.record(result)

    assert statistics.total_lines == 5
    assert statistics.parsed_lines == 4
    assert statistics.skipped_lines == 1
    assert statistics.unknown_format_lines == 1
    assert statistics.malformed_lines == 0
    assert statistics.parser_errors == 0


if __name__ == "__main__":
    test_parsing_statistics()
    print("Parsing statistics test passed.")