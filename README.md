# AI OEM Helper

An AI-powered automotive assistant that helps technicians identify OEM part number candidates using natural language vehicle requests in Arabic or English.

## Overview

AI OEM Helper processes vehicle and spare-part requests, extracts structured vehicle information using an LLM, validates the request, and searches an automotive catalog through the FAPI integration.

The system returns OEM part number candidates with clear verification warnings to avoid presenting unconfirmed compatibility as guaranteed fitment.

## Features

- Arabic and English natural-language input.
- Vehicle information extraction using LLM providers.
- Vehicle request validation and clarification handling.
- Manufacturer, model, and modification resolution.
- Automotive catalog lookup and OEM record parsing.
- Duplicate OEM record removal.
- Retry handling for transient catalog API failures.
- Explicit handling of quota and service errors.
- FastAPI REST API.
- Streamlit user interface.
- Mock-based testing without consuming external API credits.

## Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  v
FastAPI
  |
  v
Orchestrator
  |
  +---- LLM Provider
  |       |
  |       +---- Groq
  |       +---- Gemini
  |
  +---- Validation Service
  |
  +---- Catalog Lookup Service
          |
          +---- Modification Service
          |
          +---- Catalog Service
          |
          +---- FAPI Adapter
                  |
                  v
             Automotive Catalog
  |
  v
Response Builder
  |
  v
OEM Candidate Results
```

## Technology Stack

- **Language:** Python 3.11
- **API:** FastAPI
- **Frontend:** Streamlit
- **Validation:** Pydantic
- **HTTP Client:** HTTPX
- **LLM Providers:** Groq and Google Gemini
- **Automotive Data:** FAPI
- **Testing:** Pytest

## Project Structure

```text
AI-OEM-Helper/
├── docs/
├── frontend/
│   ├── app.py
│   └── mock_api.py
├── src/
│   ├── api/
│   ├── integrations/
│   ├── llm/
│   ├── models/
│   ├── services/
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11
- Valid API credentials for the selected LLM provider.
- FAPI API credentials for live automotive catalog lookup.

## Installation

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd AI-OEM-Helper
```

Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
```

Update `.env` with your own credentials:

```env
LLM_PROVIDER=groq

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

FAPI_API_KEY=your_fapi_api_key
```

Never commit `.env` or expose API credentials.

## Running the Application

### 1. Start FastAPI

```bash
uvicorn src.api.app:app --reload --port 8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 2. Start Streamlit

Open another terminal:

```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

Open:

```text
http://localhost:8501
```

## API Usage

**Endpoint**

```http
POST /api/v1/lookup
```

**Request**

```json
{
  "message": "هوبات كامري 2026 أمامي"
}
```

**Example response structure**

```json
{
  "status": "found",
  "response": "OEM candidate results...",
  "catalog_result": {
    "status": "found",
    "parts": []
  }
}
```

## Testing

The project includes unit and integration tests using mock adapters and local test data.

Run the safe test suite:

```bash
pytest -v \
  test_fapi_adapter_mock.py \
  test_modification_service.py \
  test_catalog_service.py \
  test_oem_parser.py \
  test_catalog_lookup_service.py \
  test_orchestrator_integration.py \
  test_api.py
```

Live FAPI and LLM diagnostic scripts are excluded from this test command because they may consume external API credits.

## Important Compatibility Notes

- OEM records are treated as catalog candidates, not guaranteed fitment confirmations.
- Vehicle make, model, and year may not be sufficient to establish exact compatibility.
- Engine, trim, drivetrain, market, and VIN may be required for further verification.
- The catalog data must remain the source of truth for OEM numbers.
- The LLM is responsible for extraction and interpretation, not inventing OEM part numbers.

## Project Documentation

Detailed project documentation is available in the `docs/` directory:

- Task Description
- Problem Analysis
- Requirements
- System Workflow

## Project Status

Core backend, catalog lookup workflow, API, and frontend have been implemented.

The local mocked test suite currently passes all 26 tests.
