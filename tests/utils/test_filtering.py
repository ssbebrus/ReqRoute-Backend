import pytest

from app.utils import filtering


class _ColumnStub:
    def __init__(self):
        self.ilike_calls = []
        self.eq_calls = []

    def ilike(self, pattern):
        self.ilike_calls.append(pattern)
        return ("ilike", pattern)

    def __eq__(self, value):
        self.eq_calls.append(value)
        return ("eq", value)


class _StmtStub:
    def __init__(self):
        self.offset_value = None
        self.limit_value = None
        self.order_by_calls = []
        self.where_calls = []

    def where(self, expr):
        self.where_calls.append(expr)
        return self

    def order_by(self, expr):
        self.order_by_calls.append(expr)
        return self

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self


class _ResultStub:
    def __init__(self, values):
        self._values = list(values)

    def unique(self):
        return self

    def scalars(self):
        return self

    def all(self):
        return list(self._values)


def _make_model():
    class _Model:
        pass

    model = _Model()
    model.name = _ColumnStub()
    model.title = _ColumnStub()
    return model


def test_apply_filters_handles_contains_sort_and_equals(monkeypatch):
    model = _make_model()
    stmt = _StmtStub()

    monkeypatch.setattr(filtering, "desc", lambda col: ("desc", col))

    params = {
        "name_contains": "abc",
        "title": "hello",
        "sort": "-name",
        "ignored_none": None,
    }

    result = filtering.apply_filters(model, stmt, params)

    assert result is stmt
    assert model.name.ilike_calls == ["%abc%"]
    assert model.title.eq_calls == ["hello"]
    assert stmt.order_by_calls == [("desc", model.name)]
    assert len(stmt.where_calls) == 2


def test_apply_filters_orders_ascending_when_sort_without_dash(monkeypatch):
    model = _make_model()
    stmt = _StmtStub()

    monkeypatch.setattr(filtering, "desc", lambda col: ("desc", col))

    filtering.apply_filters(model, stmt, {"sort": "title"})

    assert stmt.order_by_calls == [model.title]


@pytest.mark.asyncio
async def test_filter_and_paginate_applies_filters_and_paginates(monkeypatch):
    stmt = _StmtStub()
    model = object()

    # capture that apply_filters was invoked
    called = {}

    def fake_apply_filters(model_arg, stmt_arg, params_arg):
        called["model"] = model_arg
        called["params"] = params_arg
        return stmt_arg

    monkeypatch.setattr(filtering, "apply_filters", fake_apply_filters)
    monkeypatch.setattr(filtering, "select", lambda model_arg: stmt)

    db_execute = _ResultStub([1, 2, 3, 4])
    db_execute_second = _ResultStub(["a", "b"])

    class _DB:
        def __init__(self):
            self.calls = []

        async def execute(self, stmt_arg):
            self.calls.append(stmt_arg)
            return db_execute if len(self.calls) == 1 else db_execute_second

    db = _DB()

    params = {"page": 2, "page_size": 2, "extra": "value"}
    result = await filtering.filter_and_paginate(model, db, params)

    assert called["model"] is model
    assert called["params"] == params
    assert result["total"] == 4
    assert result["page"] == 2
    assert result["page_size"] == 2
    assert result["items"] == ["a", "b"]
    assert stmt.offset_value == 2
    assert stmt.limit_value == 2

