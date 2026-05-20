from typing import Any, cast

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

import data_analyst_agent.orchestrator as orchestrator

MODEL = cast(BaseChatModel, object())


class FakeGraph:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(state)
        return self.response


def initial_state(data_raw: dict[str, Any]) -> orchestrator.OrchestrationState:
    return {
        "data_raw": data_raw,
        "user_instructions": "standard cleaning",
        "max_retries": 3,
        "retry_count": 0,
        "pii_flagged_columns": [],
        "data_cleaned": None,
        "cleaning_response": {},
        "eda_response": {},
    }


def test_orchestrator_runs_cleaning_then_eda(monkeypatch):
    raw_data = {"sales": {0: "10", 1: "20"}}
    cleaned_data = {"sales": {0: 10, 1: 20}}
    eda_response = {
        "summary": "Sales are clean.",
        "recommendations": ["Review regional performance."],
        "results": {"profile_dataset": {"rows": 2}},
    }
    cleaning_graph = FakeGraph({"data_cleaned": cleaned_data})
    eda_graph = FakeGraph(eda_response)

    monkeypatch.setattr(
        orchestrator,
        "make_lightweight_data_cleaning_agent",
        lambda model, checkpointer=None: cleaning_graph,
    )
    monkeypatch.setattr(
        orchestrator,
        "make_eda_baseline_workflow",
        lambda model, checkpointer=None: eda_graph,
    )

    graph = orchestrator.make_data_analyst_agent(model=MODEL)
    response = graph.invoke(initial_state(raw_data))

    assert cleaning_graph.calls == [
        {
            "user_instructions": "standard cleaning",
            "source_df": raw_data,
            "max_retries": 3,
            "retry_count": 0,
        }
    ]
    assert eda_graph.calls == [{"dataframe_dict": cleaned_data}]
    assert response["data_cleaned"] == cleaned_data
    assert response["eda_response"] == eda_response


@pytest.mark.parametrize("cleaned_data", [None, {}])
def test_orchestrator_skips_eda_when_cleaning_has_no_data(
    monkeypatch,
    cleaned_data,
):
    cleaning_graph = FakeGraph({"data_cleaned": cleaned_data})
    eda_graph = FakeGraph({"summary": "should not run"})

    monkeypatch.setattr(
        orchestrator,
        "make_lightweight_data_cleaning_agent",
        lambda model, checkpointer=None: cleaning_graph,
    )
    monkeypatch.setattr(
        orchestrator,
        "make_eda_baseline_workflow",
        lambda model, checkpointer=None: eda_graph,
    )

    graph = orchestrator.make_data_analyst_agent(model=MODEL)
    response = graph.invoke(initial_state({"sales": {0: "10"}}))

    assert eda_graph.calls == []
    assert response["eda_response"] == {}


@pytest.mark.parametrize("error_key", ["cleaning_plan_error", "data_cleaner_error"])
def test_orchestrator_skips_eda_when_cleaning_has_error(monkeypatch, error_key):
    cleaning_graph = FakeGraph(
        {
            "data_cleaned": {"sales": {0: 10}},
            error_key: "cleaning failed",
        }
    )
    eda_graph = FakeGraph({"summary": "should not run"})

    monkeypatch.setattr(
        orchestrator,
        "make_lightweight_data_cleaning_agent",
        lambda model, checkpointer=None: cleaning_graph,
    )
    monkeypatch.setattr(
        orchestrator,
        "make_eda_baseline_workflow",
        lambda model, checkpointer=None: eda_graph,
    )

    graph = orchestrator.make_data_analyst_agent(model=MODEL)
    response = graph.invoke(initial_state({"sales": {0: "10"}}))

    assert eda_graph.calls == []
    assert response["eda_response"] == {}


def test_orchestrator_blocks_pii_before_subgraphs(monkeypatch):
    cleaning_graph = FakeGraph({"data_cleaned": {"sales": {0: 10}}})
    eda_graph = FakeGraph({"summary": "should not run"})

    monkeypatch.setattr(
        orchestrator,
        "make_lightweight_data_cleaning_agent",
        lambda model, checkpointer=None: cleaning_graph,
    )
    monkeypatch.setattr(
        orchestrator,
        "make_eda_baseline_workflow",
        lambda model, checkpointer=None: eda_graph,
    )

    graph = orchestrator.make_data_analyst_agent(model=MODEL)
    response = graph.invoke(initial_state({"email": {0: "a@example.com"}}))

    assert response["pii_flagged_columns"] == ["email"]
    assert cleaning_graph.calls == []
    assert eda_graph.calls == []
