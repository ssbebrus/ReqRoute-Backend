from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.models.case import Case
from app.models.checkpoint import Checkpoint
from app.models.student import Student
from app.models.team import Team
from app.models.term import SeasonEnum, Term
from app.schemas.case import CaseCreate, CaseUpdate
from app.schemas.checkpoint import CheckpointCreate, CheckpointUpdate
from app.schemas.student import StudentCreate, StudentUpdate
from app.schemas.team import TeamCreate, TeamUpdate
from app.schemas.term import TermCreate, TermUpdate
from app.services import (
    case_service,
    checkpoint_service,
    student_service,
    team_service,
    term_service,
)


CREATE_SCENARIOS = [
    (
        case_service.create_case,
        Case,
        CaseCreate(term_id=1, user_id=2, title="AI project", description="desc"),
    ),
    (
        checkpoint_service.create_checkpoint,
        Checkpoint,
        CheckpointCreate(
            team_id=1,
            number=1,
            date=date(2024, 9, 1),
            project_state="start",
            mark=5,
            video_link=None,
            presentation_link=None,
            university_mark=None,
            university_comment=None,
        ),
    ),
    (
        team_service.create_team,
        Team,
        TeamCreate(title="Team Rocket", case_id=1, workspace_link=None, final_mark=0),
    ),
    (
        term_service.create_term,
        Term,
        TermCreate(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 1, 31),
            year=2024,
            season=SeasonEnum.autumn,
        ),
    ),
    (
        student_service.create_student,
        Student,
        StudentCreate(full_name="Alice"),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("create_fn, model_cls, payload", CREATE_SCENARIOS)
async def test_create_entities_share_same_contract(mock_session, create_fn, model_cls, payload):
    entity = await create_fn(mock_session, payload)

    assert isinstance(entity, model_cls)
    mock_session.add.assert_called_once_with(entity)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity
    mock_session.reset_mock()


UPDATE_SCENARIOS = [
    (case_service, "update_case", "get_case", CaseUpdate(title="Updated")),
    (checkpoint_service, "update_checkpoint", "get_checkpoint", CheckpointUpdate(mark=9)),
    (team_service, "update_team", "get_team", TeamUpdate(title="Team A")),
    (term_service, "update_term", "get_term", TermUpdate(year=2025)),
    (student_service, "update_student", "get_student", StudentUpdate(full_name="New Name")),
]


UPDATE_SCENARIOS_WITH_PARAMS = [
    (case_service, "update_case", "get_case", "case_id", CaseUpdate(title="Updated")),
    (checkpoint_service, "update_checkpoint", "get_checkpoint", "checkpoint_id", CheckpointUpdate(mark=9)),
    (team_service, "update_team", "get_team", "team_id", TeamUpdate(title="Team A")),
    (term_service, "update_term", "get_term", "term_id", TermUpdate(year=2025)),
    (student_service, "update_student", "get_student", "student_id", StudentUpdate(full_name="New Name")),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("module, updater_name, getter_name, param_name, payload", UPDATE_SCENARIOS_WITH_PARAMS)
async def test_updates_short_circuit_when_entity_missing(monkeypatch, mock_session, module, updater_name, getter_name, param_name, payload):
    monkeypatch.setattr(module, getter_name, AsyncMock(return_value=None))
    updater = getattr(module, updater_name)

    result = await updater(mock_session, **{param_name: 1}, data=payload)

    assert result is None
    assert mock_session.commit.await_count == 0


GET_SCENARIOS = [
    (case_service.get_case, "case_id", Case(term_id=1, user_id=2, title="Case", description=None)),
    (checkpoint_service.get_checkpoint, "checkpoint_id", Checkpoint(team_id=1, number=2, date=None, project_state=None, mark=10, video_link=None, presentation_link=None, university_mark=None, university_comment=None)),
    (team_service.get_team, "team_id", Team(title="Crew", case_id=1, workspace_link=None, final_mark=0)),
    (term_service.get_term, "term_id", Term(start_date=None, end_date=None, year=2024, season=SeasonEnum.spring)),
    (student_service.get_student, "student_id", Student(full_name="Bob")),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("getter, param_name, sample", GET_SCENARIOS)
async def test_get_entity_by_id_returns_scalar_one_or_none(mock_session, result_stub, getter, param_name, sample):
    mock_session.execute.return_value = result_stub([sample])

    entity = await getter(mock_session, **{param_name: 1})

    assert entity == sample
    mock_session.execute.assert_awaited_once()
    mock_session.execute.reset_mock()


@pytest.mark.asyncio
@pytest.mark.parametrize("getter, param_name, sample", GET_SCENARIOS)
async def test_get_entity_by_id_returns_none_when_not_found(mock_session, result_stub, getter, param_name, sample):
    mock_session.execute.return_value = result_stub([])

    entity = await getter(mock_session, **{param_name: 999})

    assert entity is None
    mock_session.execute.assert_awaited_once()
    mock_session.execute.reset_mock()


UPDATE_SUCCESS_SCENARIOS = [
    (case_service, "update_case", "get_case", "case_id", Case(term_id=1, user_id=2, title="Old", description=None), CaseUpdate(title="New Title")),
    (checkpoint_service, "update_checkpoint", "get_checkpoint", "checkpoint_id", Checkpoint(team_id=1, number=2, date=None, project_state=None, mark=5, video_link=None, presentation_link=None, university_mark=None, university_comment=None), CheckpointUpdate(mark=9)),
    (team_service, "update_team", "get_team", "team_id", Team(title="Old Team", case_id=1, workspace_link=None, final_mark=0), TeamUpdate(title="New Team")),
    (term_service, "update_term", "get_term", "term_id", Term(start_date=None, end_date=None, year=2024, season=SeasonEnum.spring), TermUpdate(year=2025)),
    (student_service, "update_student", "get_student", "student_id", Student(full_name="Old Name"), StudentUpdate(full_name="New Name")),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("module, updater_name, getter_name, param_name, entity, payload", UPDATE_SUCCESS_SCENARIOS)
async def test_updates_mutate_entity_when_found(monkeypatch, mock_session, module, updater_name, getter_name, param_name, entity, payload):
    monkeypatch.setattr(module, getter_name, AsyncMock(return_value=entity))
    updater = getattr(module, updater_name)

    updated = await updater(mock_session, **{param_name: 1}, data=payload)

    assert updated is entity
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity


DELETE_SCENARIOS = [
    (case_service, "delete_case", "get_case", "case_id", Case(term_id=1, user_id=2, title="Case", description=None)),
    (checkpoint_service, "delete_checkpoint", "get_checkpoint", "checkpoint_id", Checkpoint(team_id=1, number=2, date=None, project_state=None, mark=10, video_link=None, presentation_link=None, university_mark=None, university_comment=None)),
    (team_service, "delete_team", "get_team", "team_id", Team(title="Crew", case_id=1, workspace_link=None, final_mark=0)),
    (term_service, "delete_term", "get_term", "term_id", Term(start_date=None, end_date=None, year=2024, season=SeasonEnum.spring)),
    (student_service, "delete_student", "get_student", "student_id", Student(full_name="Bob")),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("module, deleter_name, getter_name, param_name, entity", DELETE_SCENARIOS)
async def test_delete_removes_entity_when_found(monkeypatch, mock_session, module, deleter_name, getter_name, param_name, entity):
    monkeypatch.setattr(module, getter_name, AsyncMock(return_value=entity))
    deleter = getattr(module, deleter_name)

    deleted = await deleter(mock_session, **{param_name: 1})

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("module, deleter_name, getter_name, param_name, entity", DELETE_SCENARIOS)
async def test_delete_returns_none_when_not_found(monkeypatch, mock_session, module, deleter_name, getter_name, param_name, entity):
    monkeypatch.setattr(module, getter_name, AsyncMock(return_value=None))
    deleter = getattr(module, deleter_name)

    deleted = await deleter(mock_session, **{param_name: 999})

    assert deleted is None
    mock_session.delete.assert_not_called()
    assert mock_session.commit.await_count == 0
