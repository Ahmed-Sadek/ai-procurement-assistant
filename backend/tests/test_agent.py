"""Unit tests for the agent module — parsing, sanitization, truncation, retry."""

import json
import pytest
from unittest.mock import MagicMock, patch

from app.agent import parse_llm_output, handle_message


# ── parse_llm_output: valid inputs ──────────────────────────────────

class TestParseLlmOutput:

    def test_valid_aggregation(self):
        raw = json.dumps({"type": "aggregation", "pipeline": [{"$count": "total"}]})
        result = parse_llm_output(raw)
        assert result["type"] == "aggregation"

    def test_valid_query(self):
        raw = json.dumps({"type": "query", "query": {"Item Name": "USB"}, "limit": 5})
        result = parse_llm_output(raw)
        assert result["type"] == "query"
        assert result["limit"] == 5

    def test_json_in_markdown_fences(self):
        raw = '```json\n{"type": "aggregation", "pipeline": [{"$limit": 5}]}\n```'
        result = parse_llm_output(raw)
        assert result["type"] == "aggregation"

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="[Ii]nvalid"):
            parse_llm_output("not json")

    def test_missing_type_raises(self):
        with pytest.raises(ValueError, match="type"):
            parse_llm_output(json.dumps({"pipeline": []}))

    def test_bad_type_value_raises(self):
        with pytest.raises(ValueError, match="type"):
            parse_llm_output(json.dumps({"type": "delete", "filter": {}}))

    def test_aggregation_missing_pipeline_raises(self):
        with pytest.raises(ValueError, match="pipeline"):
            parse_llm_output(json.dumps({"type": "aggregation"}))

    def test_query_missing_query_raises(self):
        with pytest.raises(ValueError, match="query"):
            parse_llm_output(json.dumps({"type": "query"}))


# ── Sanitization ────────────────────────────────────────────────────

class TestSanitization:

    def test_blocks_out_stage(self):
        raw = json.dumps({"type": "aggregation", "pipeline": [{"$out": "evil"}]})
        with pytest.raises(ValueError, match="[Bb]locked"):
            parse_llm_output(raw)

    def test_blocks_merge_stage(self):
        raw = json.dumps({"type": "aggregation", "pipeline": [{"$merge": {"into": "x"}}]})
        with pytest.raises(ValueError, match="[Bb]locked"):
            parse_llm_output(raw)

    def test_blocks_delete_in_query(self):
        raw = json.dumps({"type": "query", "query": {"delete": True}})
        with pytest.raises(ValueError, match="[Bb]locked"):
            parse_llm_output(raw)

    def test_blocks_drop(self):
        raw = json.dumps({"type": "query", "query": {"drop": 1}})
        with pytest.raises(ValueError, match="[Bb]locked"):
            parse_llm_output(raw)

    def test_allows_safe_aggregation(self):
        raw = json.dumps({"type": "aggregation", "pipeline": [
            {"$match": {"Total Price": {"$ne": None}}},
            {"$group": {"_id": "$Department Name", "total": {"$sum": "$Total Price"}}},
            {"$sort": {"total": -1}},
            {"$limit": 5}
        ]})
        result = parse_llm_output(raw)
        assert result["type"] == "aggregation"


# ── handle_message: flow + truncation + retry ────────────────────────

class TestHandleMessage:

    @patch("app.agent.MongoWrapper")
    @patch("app.agent.ChatOpenAI")
    def test_aggregation_flow(self, MockLLM, MockWrapper):
        query_json = json.dumps({"type": "aggregation", "pipeline": [{"$count": "total"}]})
        mock_llm = MockLLM.return_value
        mock_llm.invoke.side_effect = [
            MagicMock(content=query_json),
            MagicMock(content="There are 346,018 orders."),
        ]
        MockWrapper.return_value.run_aggregation.return_value = [{"total": 346018}]

        result = handle_message("How many orders?")
        assert "346" in result

    @patch("app.agent.MongoWrapper")
    @patch("app.agent.ChatOpenAI")
    def test_result_truncation(self, MockLLM, MockWrapper):
        """Large result sets should be truncated to MAX_RESULTS."""
        query_json = json.dumps({"type": "query", "query": {}})
        mock_llm = MockLLM.return_value
        mock_llm.invoke.side_effect = [
            MagicMock(content=query_json),
            MagicMock(content="Here are the results."),
        ]
        MockWrapper.return_value.run_query.return_value = [{"i": i} for i in range(200)]

        result = handle_message("Show all orders")
        summary_call_args = mock_llm.invoke.call_args_list[1][0][0][0].content
        assert "truncated" in summary_call_args.lower()

    @patch("app.agent.MongoWrapper")
    @patch("app.agent.ChatOpenAI")
    def test_retry_then_succeed(self, MockLLM, MockWrapper):
        valid_json = json.dumps({"type": "aggregation", "pipeline": [{"$count": "total"}]})
        mock_llm = MockLLM.return_value
        mock_llm.invoke.side_effect = [
            MagicMock(content="garbage"),
            MagicMock(content=valid_json),
            MagicMock(content="Answer."),
        ]
        MockWrapper.return_value.run_aggregation.return_value = [{"total": 1}]

        result = handle_message("test")
        assert result == "Answer."

    @patch("app.agent.MongoWrapper")
    @patch("app.agent.ChatOpenAI")
    def test_fails_after_all_retries(self, MockLLM, MockWrapper):
        mock_llm = MockLLM.return_value
        mock_llm.invoke.side_effect = [
            MagicMock(content="bad1"),
            MagicMock(content="bad2"),
            MagicMock(content="bad3"),
        ]
        result = handle_message("nonsense")
        assert "unable" in result.lower() or "error" in result.lower()
        assert mock_llm.invoke.call_count == 3

    @patch("app.agent.MongoWrapper")
    @patch("app.agent.ChatOpenAI")
    def test_sanitization_triggers_retry(self, MockLLM, MockWrapper):
        bad_json = json.dumps({"type": "aggregation", "pipeline": [{"$out": "evil"}]})
        good_json = json.dumps({"type": "aggregation", "pipeline": [{"$count": "total"}]})
        mock_llm = MockLLM.return_value
        mock_llm.invoke.side_effect = [
            MagicMock(content=bad_json),
            MagicMock(content=good_json),
            MagicMock(content="Safe answer."),
        ]
        MockWrapper.return_value.run_aggregation.return_value = [{"total": 1}]

        result = handle_message("test")
        assert result == "Safe answer."
