import re

from backend.app.models.log_event import LogEvent
from backend.app.models.normalized_evidence import NormalizedEvidence


BUILD_ID_PATTERN = re.compile(
    r"(?:build_id|buildId|build)[=: ]+([A-Za-z0-9._-]+)",
    re.IGNORECASE,
)

DEPLOYMENT_ID_PATTERN = re.compile(
    r"(?:deployment_id|deploymentId|deployment)[=: ]+([A-Za-z0-9._-]+)",
    re.IGNORECASE,
)


class EvidenceNormalizationService:
    def normalize_log_event(
        self,
        log_event: LogEvent,
        source: str = "application_log",
        layer: str = "application",
    ) -> NormalizedEvidence:
        message = log_event.message

        build_match = BUILD_ID_PATTERN.search(message)
        deployment_match = DEPLOYMENT_ID_PATTERN.search(message)

        return NormalizedEvidence(
            log_event_id=log_event.id,
            timestamp=log_event.timestamp,
            source=source,
            layer=layer,
            service=log_event.service,
            environment=log_event.environment,
            event_type=self._event_type(log_event),
            severity=self._severity(log_event.level),
            message=message,
            host=log_event.host,
            status=(
                str(log_event.status_code)
                if log_event.status_code is not None
                else None
            ),
            trace_id=log_event.trace_id,
            build_id=build_match.group(1) if build_match else None,
            deployment_id=(
                deployment_match.group(1)
                if deployment_match
                else None
            ),
        )

    @staticmethod
    def _severity(level: str) -> str:
        level = level.upper()

        if level in {"CRITICAL", "FATAL"}:
            return "critical"

        if level == "ERROR":
            return "error"

        if level in {"WARNING", "WARN"}:
            return "warning"

        if level == "DEBUG":
            return "debug"

        return "info"

    @staticmethod
    def _event_type(log_event: LogEvent) -> str:
        if log_event.status_code is not None:
            if log_event.status_code >= 500:
                return "http_server_error"

            if log_event.status_code >= 400:
                return "http_client_error"

            return "http_request"

        if log_event.exception:
            return "application_exception"

        message = log_event.message.lower()

        if "timeout" in message:
            return "timeout"

        if "failed" in message or "failure" in message:
            return "failure"

        if "started" in message:
            return "service_started"

        if "stopped" in message:
            return "service_stopped"

        return "log_event"