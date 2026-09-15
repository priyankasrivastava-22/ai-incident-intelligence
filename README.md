# AI Incident Intelligence & Root Cause Analyzer

An AI-powered incident intelligence platform for analyzing logs and operational evidence, detecting abnormal behavior, correlating related events, and supporting evidence-based root cause analysis.

The system is designed as an AI-assisted SRE investigation platform that brings together evidence from CI/CD, application, infrastructure, database, network, and other operational layers.

---

## Overview

Production incidents often generate symptoms across multiple systems.

A database problem can cause query latency, which can lead to application timeouts, HTTP 500 errors, and eventually user-facing failures. Looking at each log independently makes it difficult to determine where the incident actually started.

This project addresses that problem by building a structured incident intelligence pipeline that transforms raw operational evidence into machine-readable, normalized evidence that can later be analyzed for anomalies, relationships, causality, and probable root causes.

The goal is to help engineers answer:

- What happened?
- When did it start?
- Which system or layer was affected?
- What evidence indicates abnormal behavior?
- Which events are related?
- What is the probable origin of the incident?
- What was the downstream impact?
- What should be investigated next?
---

## Key Capabilities

### Multi-format log ingestion

Supports ingestion of operational logs through:

- Log file uploads
- Manual log submission
- `.log` files
- `.txt` files

The ingestion layer performs validation, chunked file processing, metadata tracking, and batched persistence.

### Multi-format log parsing

The parser currently supports:

- Standard application logs
- JSON logs
- HTTP access logs

Raw log lines are converted into structured `ParsedLogLine` objects.

Extracted fields can include:

- Timestamp
- Log level
- Service
- Host
- Message
- Endpoint
- HTTP method
- HTTP status code
- Response time
- Response size
- Client IP
- HTTP version
- Exception
- Trace ID

### Parsing result classification

The parser distinguishes between:

- Parsed lines
- Malformed lines
- Unknown formats
- Parser errors

Parsing statistics are tracked for processed log files, including total, parsed, skipped, malformed, unknown-format, and parser-error counts.

### Evidence normalization

Different operational sources produce different formats.

For example:
```text
Jenkins
BUILD FAILED

RHEL
Disk usage = 99%

Application
HTTP 500

Database
Query latency = 5.2 sec
````

These signals are being transformed into a common evidence representation containing fields such as:

```text
timestamp
source
layer
service
environment
event_type
severity
message
host
status
trace_id
build_id
deployment_id
```

This common representation allows evidence from different systems to be analyzed using the same downstream pipeline.

### Evidence provenance

Normalized evidence retains a relationship to its originating log event. 
This allows the investigation layer to trace:
```text
Normalized Evidence
        ↓
Original Log Event
        ↓
Original Log File
```

This is important for producing evidence-backed incident analysis rather than unsupported conclusions.

---

## System Architecture

```text
                  Incident Sources
                         |
       +-----------------+-----------------+
       |        |        |        |        |
     CI/CD     App      OS       DB      Network
       |        |        |        |        |
       +-----------------+-----------------+
                         |
                     Ingestion
                         |
                      Parsing
                         |
                   Normalization
                         |
                  Evidence Store
                         |
                     Analytics
                         |
                Anomaly Detection
                         |
                Incident Correlation
                         |
                Timeline & Causality
                         |
                 Root Cause Engine
                         |
              Evidence-based Analysis
                         |
                  AI Incident Copilot
                         |
                  Incident Report
```

The architecture separates data ingestion, processing, persistence, analytics, ML, incident intelligence, and AI responsibilities.

---

# Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL

### Data & Processing

* Structured log parsing
* Batch processing
* Chunked file processing
* Evidence normalization
* Relational evidence storage

### AI / Machine Learning

The architecture is designed to support:

* Statistical and ML-based anomaly detection
* Incident correlation
* Failure-domain analysis
* Timeline and causality analysis
* Root cause analysis
* Evidence-based AI reasoning
* LLM-powered incident investigation

### DevOps / SRE

The project focuses on practical concepts including:

* CI/CD
* Application logs
* Infrastructure failures
* Incident response
* Observability
* Reliability engineering
* Root cause analysis
* Production troubleshooting

---

## Incident Investigation Model

The system is designed around the principle that:

> **A symptom is not necessarily the root cause.**

For example:

```text
Database overload
       ↓
Query latency increases
       ↓
Application requests timeout
       ↓
HTTP 500 responses increase
       ↓
Users experience failures
```

The HTTP 500 response is an important symptom, but it may not be the originating failure.

The planned investigation pipeline uses timestamps, services, environments, traces, event types, severity, and cross-layer relationships to identify the most probable origin and downstream impact.

---

## Operational Layers

Evidence can be associated with different operational layers:

```text
Source / Code
CI / Build / Test
Artifact / Deployment
Application / Runtime
Infrastructure / OS
Network
Database / Dependencies
User / Observed Behavior
```

This allows the system to reason across technical boundaries rather than treating every log as an isolated event.

---

## Supported Log Formats

### Standard Application Log

Example:

```text
2026-09-04 10:00:01 INFO Booking service started
```

### JSON Log

Example:

```json
{
  "timestamp": "2026-09-04T10:00:02Z",
  "level": "ERROR",
  "service": "booking-api",
  "message": "Database connection failed",
  "host": "booking-01",
  "trace_id": "abc123"
}
```

### HTTP Access Log

Example:

```text
192.168.1.10 - - [04/Sep/2026:10:00:03 +0000] "GET /api/bookings HTTP/1.1" 200 1245
```

The parser extracts protocol-specific fields while converting all supported formats into a common structured representation.

---

## Data Flow

```text
Raw Log
   |
   v
Format Detection
   |
   v
ParsedLogLine
   |
   v
LogEvent
   |
   v
NormalizedEvidence
   |
   v
Analytics / ML / Incident Intelligence
```

### Raw evidence

Original source data received by the platform.

### Parsed evidence

Structured representation extracted from the original source format.

### Normalized evidence

Common representation used by downstream analytics, anomaly detection, incident correlation, and RCA components.

---
## Backend Architecture

The backend follows a layered architecture:

```text
API
 |
 v
Services
 |
 v
Repositories
 |
 v
Database
```

Specialized processing is separated into dedicated components:

```text
ingestion/
analytics/
ml/
incidents/
evidence/
ai/
workers/
```

This keeps API endpoints independent from business logic and allows individual processing components to evolve independently.

---

## Project Structure

```text
AI Incident Intelligence/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── ingestion/
│   │   ├── analytics/
│   │   ├── ml/
│   │   ├── incidents/
│   │   ├── evidence/
│   │   ├── ai/
│   │   ├── workers/
│   │   └── main.py
│   │
│   └── alembic/
│
├── frontend/
├── data/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## Engineering Considerations

### Chunked processing

Large uploaded files are processed in chunks rather than loading the complete file into memory.

### Batch persistence

Parsed log events are persisted in batches to reduce unnecessary database operations.

### Separation of concerns

Parsing, normalization, storage, analytics, ML, incident correlation, and AI analysis are kept as separate responsibilities.

### Evidence provenance

Normalized evidence maintains a link to its source event so investigation results can be traced back to the original data.

### Controlled AI context

The AI layer is designed to consume relevant structured evidence rather than unrestricted raw system data.

This helps reduce unsupported conclusions and keeps AI-generated analysis connected to observable evidence.

### Scalability

The architecture leaves room for:

* Streaming ingestion
* Background workers
* Message queues
* Pagination
* Distributed processing
* Independent analytics/ML workers
* Larger evidence volumes

These components will be introduced where required rather than added only as technology demonstrations.

---

## Security Considerations

The project is designed with security boundaries between:

* API access
* Application services
* Database access
* External configuration
* AI processing

Secrets and environment-specific configuration are kept outside source code.

The AI layer is not intended to have unrestricted database or system access.

---

## Example Incident

Consider the following evidence:

```text
10:00:01  Database CPU = 98%
10:00:04  Query latency = 5.2 sec
10:00:07  Application request timeout
10:00:08  HTTP 500 /api/bookings
10:00:10  Increased user failures
```

A traditional log search may surface the HTTP 500 errors first.

The incident intelligence pipeline is designed to connect the events:

```text
Infrastructure / Database
          ↓
      Performance
          ↓
     Application
          ↓
       HTTP 500
          ↓
      User Impact
```

The final RCA should identify the most probable originating failure, show the supporting evidence, and distinguish it from downstream symptoms.

---

## Current Implementation

The platform currently provides the foundation for:

* FastAPI backend architecture
* PostgreSQL persistence
* SQLAlchemy data models
* Alembic database migrations
* Log file ingestion
* Manual log ingestion
* Chunked file processing
* Batched event persistence
* Standard log parsing
* JSON log parsing
* HTTP access log parsing
* Parsing result classification
* Parsing statistics
* Structured log event storage
* Evidence normalization architecture
* Normalized evidence persistence model

The incident analytics, ML anomaly detection, cross-layer correlation, causality analysis, root cause engine, and AI incident copilot are being developed on top of this foundation.

---

## Future Capabilities

The platform is designed to evolve toward:

* Cross-source evidence ingestion
* Automated anomaly detection
* Incident clustering and correlation
* Incident timelines
* Cross-layer causal analysis
* Failure-domain classification
* Root cause scoring
* Evidence-based investigation recommendations
* AI-generated incident summaries
* Interactive incident investigation
* Incident dashboards
* Automated incident reports

---

## Running the Project

### Prerequisites

* Python 3.x
* PostgreSQL
* Git

### Clone the repository

```bash
git clone <repository-url>
cd "AI Incident Intelligence"
```

### Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file based on:

```text
.env.example
```

Configure the PostgreSQL connection and other application settings.

### Run database migrations

```powershell
alembic upgrade head
```

### Start the API

```powershell
uvicorn backend.app.main:app --reload
```

The FastAPI documentation will be available through the configured application URL.

---

## Testing

Parser and processing components include focused tests covering:

* Standard log parsing
* JSON log parsing
* Access log parsing
* Format routing
* Malformed input
* Unknown formats
* Parsing statistics

The test suite will expand as analytics, ML, incident correlation, and RCA components are implemented.

---

## Why This Project?

This project combines software engineering, DevOps/SRE, data processing, machine learning, and Generative AI into one operational use case.

Instead of building a generic chatbot, the system focuses on a practical engineering problem:

```text
Operational Evidence
        ↓
Structured Signals
        ↓
Incident Relationships
        ↓
Probable Root Cause
        ↓
Evidence-backed AI Analysis
```

The long-term objective is to reduce the manual effort required to investigate complex incidents and help engineers move from raw logs to actionable incident intelligence faster.

