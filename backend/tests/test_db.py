"""Unit tests for MongoWrapper using mocked MongoDB."""

import pytest
from unittest.mock import MagicMock, patch

from app.db import MongoWrapper


@pytest.fixture
def wrapper():
    with patch("app.db.get_database") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        w = MongoWrapper("purchase_orders")
        yield w


def test_run_query_basic(wrapper):
    wrapper.collection.find.return_value = [{"Item Name": "USB"}]
    results = wrapper.run_query({"Item Name": "USB"})
    wrapper.collection.find.assert_called_once_with({"Item Name": "USB"}, None)
    assert results == [{"Item Name": "USB"}]


def test_run_query_with_projection(wrapper):
    cursor = MagicMock()
    wrapper.collection.find.return_value = cursor
    cursor.__iter__ = MagicMock(return_value=iter([{"Item Name": "USB"}]))
    wrapper.run_query({"Item Name": "USB"}, projection={"Item Name": 1, "_id": 0})
    wrapper.collection.find.assert_called_once_with(
        {"Item Name": "USB"}, {"Item Name": 1, "_id": 0}
    )


def test_run_query_with_limit(wrapper):
    cursor = MagicMock()
    wrapper.collection.find.return_value = cursor
    cursor.limit.return_value = [{"a": 1}]
    wrapper.run_query({}, limit=5)
    cursor.limit.assert_called_once_with(5)


def test_run_aggregation(wrapper):
    pipeline = [{"$group": {"_id": "$Fiscal Year", "count": {"$sum": 1}}}]
    wrapper.collection.aggregate.return_value = [{"_id": "2013-2014", "count": 100}]
    results = wrapper.run_aggregation(pipeline)
    wrapper.collection.aggregate.assert_called_once_with(pipeline)
    assert results == [{"_id": "2013-2014", "count": 100}]


def test_run_aggregation_empty_pipeline(wrapper):
    wrapper.collection.aggregate.return_value = []
    results = wrapper.run_aggregation([])
    assert results == []
