import json
import re
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings
from app.db import MongoWrapper
from app.prompts import SYSTEM_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
MAX_RESULTS = 50

BLOCKED_STAGES = {"$out", "$merge"}
BLOCKED_OPS = {"$rename", "$unset"}
BLOCKED_METHODS = {"delete", "drop", "remove", "update", "insert", "replace"}


def parse_llm_output(raw: str) -> dict:
    """Extract and validate a JSON query/aggregation from the LLM response.

    Raises ValueError if the output is not valid JSON or missing required fields.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in LLM output: {raw[:200]}")

    if not isinstance(parsed, dict):
        raise ValueError(f"Invalid JSON: expected object, got {type(parsed).__name__}")

    # Validate type field
    if "type" not in parsed or parsed["type"] not in ("query", "aggregation"):
        raise ValueError(
            f"Invalid or missing 'type' field. Must be 'query' or 'aggregation', got: {parsed.get('type')}"
        )

    # Validate required fields
    if parsed["type"] == "aggregation" and "pipeline" not in parsed:
        raise ValueError("Aggregation output missing required 'pipeline' field")
    if parsed["type"] == "query" and "query" not in parsed:
        raise ValueError("Query output missing required 'query' field")

    # Sanitize: block dangerous operations
    _sanitize_parsed(parsed)

    return parsed


def _sanitize_parsed(parsed: dict) -> None:
    """Block dangerous MongoDB operations that the LLM should never generate.

    Raises ValueError if a blocked operation is detected.
    """
    raw = json.dumps(parsed).lower()
    for method in BLOCKED_METHODS:
        if method in raw:
            raise ValueError(f"Blocked operation detected: '{method}' is not allowed")

    if parsed["type"] == "aggregation":
        for stage in parsed["pipeline"]:
            for key in stage:
                if key.strip() in BLOCKED_STAGES:
                    raise ValueError(f"Blocked pipeline stage: '{key}' is not allowed")


def _clean_pipeline(pipeline: list[dict]) -> list[dict]:
    """Strip whitespace from aggregation stage keys — LLMs sometimes add spaces."""
    cleaned = []
    for stage in pipeline:
        cleaned.append({k.strip(): v for k, v in stage.items()})
    return cleaned


def _execute_parsed(parsed: dict, wrapper: MongoWrapper) -> list[dict]:
    """Dispatch the parsed JSON to the appropriate MongoWrapper method."""
    if parsed["type"] == "aggregation":
        pipeline = _clean_pipeline(parsed["pipeline"])
        return wrapper.run_aggregation(pipeline)
    else:
        return wrapper.run_query(
            query_dict=parsed["query"],
            projection=parsed.get("projection"),
            limit=parsed.get("limit", 0),
        )


def handle_message(question: str) -> str:
    """Full agent pipeline: question -> LLM -> MongoDB -> natural language answer."""
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
        max_tokens=1024,
    )
    wrapper = MongoWrapper()

    # Step 1: Ask LLM to generate a MongoDB query
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    parsed = None
    last_error = None

    for attempt in range(1 + MAX_RETRIES):
        response = llm.invoke(messages)
        raw_output = response.content

        try:
            parsed = parse_llm_output(raw_output)
            break
        except ValueError as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            # On retry, add error feedback to help the LLM correct itself
            messages.append(HumanMessage(
                content=f"Your previous response was not valid JSON. Error: {last_error}\n"
                        f"Please respond with ONLY a valid JSON object."
            ))

    if parsed is None:
        return f"Sorry, I was unable to process your question. Error: {last_error}"

    # Step 2: Execute the query
    try:
        results = _execute_parsed(parsed, wrapper)
    except Exception as e:
        logger.error(f"MongoDB execution error: {e}")
        return f"Sorry, there was an error executing the database query: {e}"

    # Truncate large result sets to avoid blowing LLM context
    truncated = False
    if len(results) > MAX_RESULTS:
        results = results[:MAX_RESULTS]
        truncated = True

    # Step 3: Summarize results in natural language
    results_str = _serialize_results(results)
    if truncated:
        results_str += f"\n\n(Note: Results truncated to first {MAX_RESULTS} of many matching documents.)"

    summary_prompt = SUMMARIZE_PROMPT.format(
        question=question,
        results=results_str,
    )

    summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
    return summary_response.content


def _serialize_results(results: list[dict]) -> str:
    """Convert MongoDB results to a JSON-safe string."""
    import bson

    def default_serializer(obj):
        if isinstance(obj, bson.ObjectId):
            return str(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    try:
        return json.dumps(results, default=default_serializer, indent=2)
    except (TypeError, ValueError):
        return str(results)
