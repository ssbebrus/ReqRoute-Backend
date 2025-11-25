from unittest.mock import AsyncMock

import pytest

from app.models.team_membership import TeamMembership
from app.schemas.team_membership import TeamMembershipCreate, TeamMembershipUpdate
from app.services import team_membership_service


@pytest.mark.asyncio
async def test_get_memberships_filtered_by_student(mock_session, result_stub):
    memberships = [TeamMembership(student_id=1, team_id=2, role="Lead", group="A-1")]
    mock_session.execute.return_value = result_stub(memberships)

    result = await team_membership_service.get_memberships_student(mock_session, student_id=1)

    assert result == memberships
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_memberships_filtered_by_team(mock_session, result_stub):
    memberships = [TeamMembership(student_id=4, team_id=5, role=None, group="B-2")]
    mock_session.execute.return_value = result_stub(memberships)

    result = await team_membership_service.get_memberships_team(mock_session, team_id=5)

    assert result == memberships
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_membership_persists_entity(mock_session):
    payload = TeamMembershipCreate(student_id=3, team_id=6, role="Researcher", group="G-7")

    membership = await team_membership_service.create_membership(mock_session, payload)

    assert isinstance(membership, TeamMembership)
    assert membership.group == "G-7"
    mock_session.add.assert_called_once_with(membership)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is membership


@pytest.mark.asyncio
async def test_update_membership_missing(monkeypatch, mock_session):
    monkeypatch.setattr(team_membership_service, "get_membership", AsyncMock(return_value=None))

    result = await team_membership_service.update_membership(
        mock_session,
        membership_id=123,
        data=TeamMembershipUpdate(role="Mentor"),
    )

    assert result is None
    assert mock_session.commit.await_count == 0


@pytest.mark.asyncio
async def test_delete_membership_invokes_session(monkeypatch, mock_session):
    entity = TeamMembership(student_id=7, team_id=8, role=None, group="K-9")
    monkeypatch.setattr(team_membership_service, "get_membership", AsyncMock(return_value=entity))

    deleted = await team_membership_service.delete_membership(mock_session, membership_id=1)

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_all_memberships_returns_scalars(mock_session, result_stub):
    stored = [
        TeamMembership(student_id=1, team_id=2, role="Lead", group="A-1"),
        TeamMembership(student_id=3, team_id=4, role="Member", group="B-2"),
    ]
    mock_session.execute.return_value = result_stub(stored)

    memberships = await team_membership_service.get_all_memberships(mock_session)

    assert memberships == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_membership_returns_scalar_one_or_none(mock_session, result_stub):
    stored = TeamMembership(student_id=1, team_id=2, role="Lead", group="A-1")
    mock_session.execute.return_value = result_stub([stored])

    membership = await team_membership_service.get_membership(mock_session, membership_id=1)

    assert membership == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_membership_returns_none_when_not_found(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([])

    membership = await team_membership_service.get_membership(mock_session, membership_id=999)

    assert membership is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_membership_mutates_entity(monkeypatch, mock_session):
    entity = TeamMembership(student_id=1, team_id=2, role="Old Role", group="A-1")
    monkeypatch.setattr(team_membership_service, "get_membership", AsyncMock(return_value=entity))
    patch = TeamMembershipUpdate(role="New Role")

    updated = await team_membership_service.update_membership(mock_session, membership_id=1, data=patch)

    assert updated is entity
    assert updated.role == "New Role"
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity
