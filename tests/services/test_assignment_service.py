from unittest.mock import AsyncMock

import pytest

from app.models.assignment import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate
from app.services import assignment_service


@pytest.mark.asyncio
async def test_get_all_assignments_returns_scalars(mock_session, result_stub):
    stored = [Assignment(meeting_id=1, text="Discuss scope", completed=False)]
    mock_session.execute.return_value = result_stub(stored)

    assignments = await assignment_service.get_all_assignments(mock_session)

    assert assignments == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_assignments_on_meeting_filters(mock_session, result_stub):
    stored = [Assignment(meeting_id=2, text="Prepare deck", completed=None)]
    mock_session.execute.return_value = result_stub(stored)

    assignments = await assignment_service.get_all_assignments_on_meeting(mock_session, meeting_id=2)

    assert assignments[0].meeting_id == 2
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_assignment_persists_entity(mock_session):
    payload = AssignmentCreate(meeting_id=3, text="Draft plan", completed=False)

    assignment = await assignment_service.create_assignment(mock_session, payload)

    assert assignment.text == payload.text
    mock_session.add.assert_called_once_with(assignment)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is assignment


@pytest.mark.asyncio
async def test_update_assignment_mutates_entity(monkeypatch, mock_session):
    entity = Assignment(meeting_id=4, text="Draft", completed=False)
    monkeypatch.setattr(
        assignment_service,
        "get_assignment",
        AsyncMock(return_value=entity),
    )
    patch = AssignmentUpdate(text="Updated draft", completed=True)

    updated = await assignment_service.update_assignment(mock_session, assignment_id=1, data=patch)

    assert updated.text == "Updated draft"
    assert updated.completed is True
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity


@pytest.mark.asyncio
async def test_update_assignment_handles_missing(monkeypatch, mock_session):
    monkeypatch.setattr(
        assignment_service,
        "get_assignment",
        AsyncMock(return_value=None),
    )
    patch = AssignmentUpdate(text="does not matter")

    updated = await assignment_service.update_assignment(mock_session, assignment_id=99, data=patch)

    assert updated is None
    assert mock_session.commit.await_count == 0


@pytest.mark.asyncio
async def test_delete_assignment_removes_entity(monkeypatch, mock_session):
    entity = Assignment(meeting_id=5, text="Wrap up", completed=None)
    monkeypatch.setattr(
        assignment_service,
        "get_assignment",
        AsyncMock(return_value=entity),
    )

    deleted = await assignment_service.delete_assignment(mock_session, assignment_id=5)

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_delete_assignment_missing_is_safe(monkeypatch, mock_session):
    monkeypatch.setattr(
        assignment_service,
        "get_assignment",
        AsyncMock(return_value=None),
    )

    deleted = await assignment_service.delete_assignment(mock_session, assignment_id=404)

    assert deleted is None
    mock_session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_get_assignment_returns_scalar_one_or_none(mock_session, result_stub):
    stored = Assignment(meeting_id=1, text="Get this", completed=False)
    mock_session.execute.return_value = result_stub([stored])

    assignment = await assignment_service.get_assignment(mock_session, assignment_id=1)

    assert assignment == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_assignment_returns_none_when_not_found(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([])

    assignment = await assignment_service.get_assignment(mock_session, assignment_id=999)

    assert assignment is None
    mock_session.execute.assert_awaited_once()
