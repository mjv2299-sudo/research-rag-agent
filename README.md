# Web RAG Research Agent (FastAPI + OpenAI)

## Overview

This project implements a **Web-based Retrieval-Augmented Generation (RAG) Research Agent** using **Python, FastAPI, and the OpenAI API**.
The agent accepts a research question, performs controlled web searches, synthesizes information from credible sources, and returns a **structured JSON response with citations**.

The system is designed to be **cost-efficient, reliable, and production-friendly**, with features such as caching, schema validation, and controlled search limits.

---

# Features

* **Web-based RAG** – Retrieves live information using the `web_search` tool.
* **Query Planner** – Generates targeted search queries before researching.
* **Structured Output** – Responses follow a strict JSON schema.
* **Source Citations** – Each claim includes supporting sources.
* **Cost Control** – Limits web searches and token usage.
* **Caching** – Prevents repeated API calls for the same question.
* **JSON Repair** – Automatically fixes truncated JSON outputs if needed.
* **FastAPI Interface** – Easy REST API for integration.

---

# Architecture

```
User Question
      │
      ▼
FastAPI Endpoint (/research)
      │
      ▼
Research Agent
      │
      ├─ Query Planner (LLM)
      │      │
      │      ▼
      │   Search Queries
      │
      ├─ Web Search Tool
      │
      ├─ LLM Research & Synthesis
      │
      ▼
Structured JSON Output
      │
      ▼
Cache (DiskCache)
      │
      ▼
API Response
```

---

# Project Structure

```
research-agent/
│
├── app/
│   ├── main.py        # FastAPI server and API endpoints
│   ├── agent.py       # Core research agent logic
│   ├── schemas.py     # Pydantic data models
│   ├── cache.py       # Disk cache implementation
│   └── config.py      # Environment variable loader
│
├── requirements.txt
├── .env
└── README.md
```

---

# Requirements

* Python **3.9+**
* OpenAI API key
* Internet connection

Python libraries:

* fastapi
* uvicorn
* openai
* pydantic
* python-dotenv
* diskcache

---

# Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/research-agent.git
cd research-agent
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate environment:

**Windows**

```bash
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file in the project root.

```
OPENAI_API_KEY=your_openai_api_key

MODEL=gpt-4o-mini
MAX_SEARCHES=2
MAX_OUTPUT_TOKENS=1600

CACHE_TTL_SECONDS=86400
```

### Configuration Explanation

| Variable          | Description                       |
| ----------------- | --------------------------------- |
| OPENAI_API_KEY    | Your OpenAI API key               |
| MODEL             | Model used for reasoning          |
| MAX_SEARCHES      | Maximum web searches per question |
| MAX_OUTPUT_TOKENS | Maximum response size             |
| CACHE_TTL_SECONDS | Cache duration (in seconds)       |

---

# Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

Open interactive API docs:

```
http://127.0.0.1:8000/docs
```

---

# API Usage

### Endpoint

```
POST /research
```

### Request Body

```json
{
  "question": "What are the main requirements of the EU AI Act for high-risk systems?"
}
```

### Example Response

```json
{
  "answer_bullets": [
    "High-risk AI systems must implement risk management systems.",
    "Systems must maintain technical documentation and logs.",
    "Human oversight must be enabled."
  ],
  "claims": [
    {
      "claim": "High-risk AI systems require risk management procedures.",
      "confidence": 0.92,
      "citations": [
        {
          "url": "https://example.com",
          "title": "EU AI Act Overview",
          "publisher": "European Commission",
          "published_date": "2024"
        }
      ]
    }
  ],
  "sources": [],
  "open_questions": []
}
```

---

# Cost Optimization

The system includes multiple safeguards to control API costs.

### Search Limits

Maximum web searches per question:

```
MAX_SEARCHES=2
```

### Caching

Repeated questions are served from cache instead of triggering new API calls.

### Token Limits

Responses are constrained to prevent excessive output.

---

# Safe Example Questions

Recommended test queries:

* What are the main requirements for high-risk AI systems under the EU AI Act?
* What are the key obligations of GDPR for data controllers?
* What is the latest GDP growth rate of India?
* What are the benefits and risks of nuclear energy?

Avoid extremely broad questions such as:

* "Explain everything about AI."

---

# Future Improvements

Possible enhancements:

* Vector database integration (Hybrid RAG)
* Multi-step autonomous research
* Source credibility ranking
* Streaming responses
* Frontend dashboard
* Cost monitoring

---

# License

This project is intended for educational and experimental purposes.

---

# Acknowledgements

* OpenAI API
* FastAPI
* Pydantic
* DiskCache
