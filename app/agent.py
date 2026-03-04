import os
import hashlib
from openai import OpenAI
from .schemas import PlannerOut, ResearchReport
from .cache import get_cache, set_cache

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_SEARCHES = int(os.getenv("MAX_SEARCHES", "2"))  # cost lever
# Increase a bit so JSON reliably completes (still cost-effective)
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1600"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

def _key(question: str) -> str:
    return hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()

def _report_schema():
    # Strict schema: every property must be required in nested objects.
    return {
        "name": "research_report",
        "schema": {
            "type": "object",
            "properties": {
                "answer_bullets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 12
                },
                "claims": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "citations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string"},
                                        "title": {"type": "string"},
                                        "publisher": {"type": "string"},
                                        "published_date": {"type": "string"}
                                    },
                                    "required": ["url", "title", "publisher", "published_date"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["claim", "confidence", "citations"],
                        "additionalProperties": False
                    }
                },
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "title": {"type": "string"},
                            "publisher": {"type": "string"},
                            "published_date": {"type": "string"}
                        },
                        "required": ["url", "title", "publisher", "published_date"],
                        "additionalProperties": False
                    }
                },
                "open_questions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["answer_bullets", "claims", "sources", "open_questions"],
            "additionalProperties": False
        },
        "strict": True
    }

async def plan_queries(question: str) -> PlannerOut:
    planner_schema = {
        "name": "planner_out",
        "schema": {
            "type": "object",
            "properties": {
                "search_queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 4
                },
                "must_answer": {"type": "array", "items": {"type": "string"}},
                "excluded": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["search_queries", "must_answer", "excluded"],
            "additionalProperties": False,
        },
        "strict": True
    }

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content":
                "You are a research query planner. Produce 2–4 targeted web search queries. "
                "Prefer primary/official sources. Return ONLY JSON matching schema."
            },
            {"role": "user", "content": question},
        ],
        text={"format": {"type": "json_schema", **planner_schema}},
        max_output_tokens=300,
    )
    return PlannerOut.model_validate_json(resp.output_text)

async def _repair_json(bad_text: str) -> str:
    schema = _report_schema()
    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content":
                "You repair invalid JSON into valid JSON matching the schema. Output ONLY JSON."
            },
            {"role": "user", "content": f"Fix this JSON:\n{bad_text}"},
        ],
        text={"format": {"type": "json_schema", **schema}},
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    return resp.output_text

async def run_research(question: str) -> ResearchReport:
    q = question.strip()
    if not q:
        raise ValueError("Empty question")

    k = _key(q)
    cached = get_cache(k)
    if cached:
        return ResearchReport.model_validate(cached)

    planner = await plan_queries(q)
    search_list = "\n".join(f"- {s}" for s in planner.search_queries)

    schema = _report_schema()

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content":
                f"You are a research agent. You MUST do at most {MAX_SEARCHES} web_search calls. "
                "Every factual claim must have citations from web results. Prefer primary sources. "
                "If published_date is unknown, return empty string \"\".\n\n"
                "Output rules:\n"
                "- Return ONLY JSON matching the schema.\n"
                "- Keep answer_bullets short (1–2 lines each).\n"
                "- claims max 8.\n"
            },
            {"role": "user", "content":
                f"Question: {q}\n\n"
                "Use these search queries (<= 1 web_search per query; stop early if enough):\n"
                f"{search_list}"
            },
        ],
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **schema}},
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    raw = resp.output_text

    # Validate; if parsing fails, do ONE repair attempt (no web_search, cheap)
    try:
        report = ResearchReport.model_validate_json(raw)
    except Exception:
        repaired = await _repair_json(raw)
        report = ResearchReport.model_validate_json(repaired)

    set_cache(k, report.model_dump(), ttl=CACHE_TTL_SECONDS)
    return report