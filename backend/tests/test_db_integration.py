"""Integration tests against live MongoDB with seeded purchase order data."""

import pytest
from app.db import MongoWrapper

TOTAL_RECORDS = 346018


@pytest.fixture(scope="module")
def wrapper():
    return MongoWrapper("purchase_orders")


def test_total_record_count(wrapper):
    count = wrapper.collection.count_documents({})
    assert count == TOTAL_RECORDS


def test_fiscal_years(wrapper):
    years = sorted(wrapper.collection.distinct("Fiscal Year"))
    assert "2012-2013" in years
    assert "2013-2014" in years
    assert "2014-2015" in years


@pytest.mark.parametrize("acq_type", [
    "IT Goods", "IT Services", "IT Telecommunications",
    "NON-IT Goods", "NON-IT Services",
])
def test_acquisition_types_exist(wrapper, acq_type):
    assert wrapper.collection.count_documents({"Acquisition Type": acq_type}) > 0


def test_query_known_record(wrapper):
    results = wrapper.run_query({
        "Purchase Order Number": "REQ0011118",
        "Supplier Name": "Pitney Bowes",
    })
    assert len(results) >= 1
    assert results[0]["Item Name"] == "USB"


def test_query_with_projection(wrapper):
    results = wrapper.run_query(
        {"Acquisition Type": "IT Goods"},
        projection={"Item Name": 1, "_id": 0},
        limit=3,
    )
    assert len(results) > 0
    for doc in results:
        assert "Item Name" in doc
        assert "_id" not in doc


def test_aggregation_top_departments(wrapper):
    pipeline = [
        {"$group": {"_id": "$Department Name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3},
    ]
    results = wrapper.run_aggregation(pipeline)
    assert len(results) == 3
    assert results[0]["_id"] == "Corrections and Rehabilitation, Department of"


def test_aggregation_count_by_fiscal_year(wrapper):
    pipeline = [
        {"$group": {"_id": "$Fiscal Year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    results = wrapper.run_aggregation(pipeline)
    total = sum(r["count"] for r in results)
    assert total == TOTAL_RECORDS


def test_quarter_field_exists(wrapper):
    doc = wrapper.run_query({"Quarter": {"$ne": None}}, limit=1)
    assert len(doc) == 1
    assert "Q" in doc[0]["Quarter"]


def test_types_are_correct(wrapper):
    from datetime import datetime
    doc = wrapper.run_query({"Creation Date": {"$ne": None}}, limit=1)[0]
    assert isinstance(doc["Creation Date"], datetime)
    assert isinstance(doc["Total Price"], (int, float))
    assert isinstance(doc["Quantity"], (int, float))
