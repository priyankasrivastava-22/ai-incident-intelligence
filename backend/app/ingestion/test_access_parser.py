from backend.app.ingestion.access_parser import AccessLogParser


parser = AccessLogParser()

access_log = (
    '192.168.1.10 - - '
    '[04/Sep/2026:10:00:03 +0000] '
    '"GET /api/bookings HTTP/1.1" '
    '200 1245'
)

result = parser.parse(access_log)

print(result)

if result.parsed_log:
    print("Client IP:", result.parsed_log.client_ip)
    print("Timestamp:", result.parsed_log.timestamp)
    print("Method:", result.parsed_log.method)
    print("Endpoint:", result.parsed_log.endpoint)
    print("HTTP Version:", result.parsed_log.http_version)
    print("Status:", result.parsed_log.status_code)
    print("Response Size:", result.parsed_log.response_size)