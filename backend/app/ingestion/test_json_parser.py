from backend.app.ingestion.parser import LogParser
from backend.app.ingestion.parser_models import ParseStatus


parser = LogParser()


standard_log = (
    "2026-09-04 10:00:01 INFO "
    "Booking service started"
)

json_log = """
{
    "timestamp": "2026-09-04T10:00:02Z",
    "level": "ERROR",
    "service": "booking-api",
    "message": "Database connection failed",
    "host": "booking-01",
    "trace_id": "abc123"
}
"""

access_log = (
    '192.168.1.10 - - '
    '[04/Sep/2026:10:00:03 +0000] '
    '"GET /api/bookings HTTP/1.1" '
    '200 1245'
)


def test_parser_routing() -> None:
    standard_result = parser.parse_with_result(standard_log)
    json_result = parser.parse_with_result(json_log)
    access_result = parser.parse_with_result(access_log)

    print("\nSTANDARD:")
    print(standard_result)

    print("\nJSON:")
    print(json_result)

    print("\nACCESS:")
    print(access_result)

    assert standard_result.status == ParseStatus.PARSED
    assert json_result.status == ParseStatus.PARSED
    assert access_result.status == ParseStatus.PARSED

    assert standard_result.parsed_log is not None
    assert json_result.parsed_log is not None
    assert access_result.parsed_log is not None

    assert standard_result.parsed_log.message == "Booking service started"

    assert json_result.parsed_log.level == "ERROR"
    assert json_result.parsed_log.trace_id == "abc123"

    assert access_result.parsed_log.client_ip == "192.168.1.10"
    assert access_result.parsed_log.endpoint == "/api/bookings"
    assert access_result.parsed_log.status_code == 200


if __name__ == "__main__":
    test_parser_routing()