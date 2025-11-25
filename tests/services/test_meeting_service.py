import datetime
from unittest.mock import AsyncMock

import pytest

from app.models.meeting import Meeting, MeetingUser
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.schemas.meeting_user import MeetingUserCreate
from app.services import meeting_service


@pytest.mark.asyncio
async def test_get_previous_meeting_id_uses_scalar(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([7])

    previous_id = await meeting_service.get_previous_meeting_id(mock_session, meeting_id=10)

    assert previous_id == 7
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_link_meeting_user_creates_relation(mock_session):
    payload = MeetingUserCreate(meeting_id=1, user_id=5)

    link = await meeting_service.link_meeting_user(mock_session, payload)

    assert isinstance(link, MeetingUser)
    assert link.meeting_id == 1
    mock_session.add.assert_called_once_with(link)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is link


@pytest.mark.asyncio
async def test_create_meeting_persists_entity(mock_session):
    payload = MeetingCreate(
        team_id=2,
        previous_meeting_id=None,
        recording_link=None,
        date_time=datetime.datetime(2024, 9, 1, 12, 0),
        summary="Kick-off",
    )

    meeting = await meeting_service.create_meeting(mock_session, payload)

    assert isinstance(meeting, Meeting)
    assert meeting.summary == "Kick-off"
    mock_session.add.assert_called_once_with(meeting)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is meeting


@pytest.mark.asyncio
async def test_update_meeting_handles_missing(monkeypatch, mock_session):
    monkeypatch.setattr(meeting_service, "get_meeting", AsyncMock(return_value=None))

    updated = await meeting_service.update_meeting(
        mock_session,
        meeting_id=100,
        data=MeetingUpdate(summary="Later"),
    )

    assert updated is None
    assert mock_session.commit.await_count == 0


@pytest.mark.asyncio
async def test_delete_meeting_invokes_session(monkeypatch, mock_session):
    entity = Meeting(
        team_id=3,
        previous_meeting_id=None,
        recording_link=None,
        date_time=datetime.datetime.now(datetime.timezone.utc),
        summary=None,
    )
    monkeypatch.setattr(meeting_service, "get_meeting", AsyncMock(return_value=entity))

    deleted = await meeting_service.delete_meeting(mock_session, meeting_id=entity.id if hasattr(entity, "id") else 1)

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_all_meetings_returns_scalars(mock_session, result_stub):
    stored = [
        Meeting(team_id=1, previous_meeting_id=None, recording_link=None, date_time=datetime.datetime.now(datetime.timezone.utc), summary="First"),
        Meeting(team_id=2, previous_meeting_id=None, recording_link=None, date_time=datetime.datetime.now(datetime.timezone.utc), summary="Second"),
    ]
    mock_session.execute.return_value = result_stub(stored)

    meetings = await meeting_service.get_all_meetings(mock_session)

    assert meetings == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_meetings_on_team_filters(mock_session, result_stub):
    stored = [Meeting(team_id=5, previous_meeting_id=None, recording_link=None, date_time=datetime.datetime.now(datetime.timezone.utc), summary="Team 5")]
    mock_session.execute.return_value = result_stub(stored)

    meetings = await meeting_service.get_all_meetings_on_team(mock_session, team_id=5)

    assert meetings[0].team_id == 5
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_meeting_returns_scalar_one_or_none(mock_session, result_stub):
    stored = Meeting(team_id=1, previous_meeting_id=None, recording_link=None, date_time=datetime.datetime.now(datetime.timezone.utc), summary="Test")
    mock_session.execute.return_value = result_stub([stored])

    meeting = await meeting_service.get_meeting(mock_session, meeting_id=1)

    assert meeting == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_meeting_returns_none_when_not_found(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([])

    meeting = await meeting_service.get_meeting(mock_session, meeting_id=999)

    assert meeting is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_meeting_mutates_entity(monkeypatch, mock_session):
    entity = Meeting(
        team_id=2,
        previous_meeting_id=None,
        recording_link=None,
        date_time=datetime.datetime.now(datetime.timezone.utc),
        summary="Old summary",
    )
    monkeypatch.setattr(meeting_service, "get_meeting", AsyncMock(return_value=entity))
    patch = MeetingUpdate(summary="New summary")

    updated = await meeting_service.update_meeting(mock_session, meeting_id=1, data=patch)

    assert updated is entity
    assert updated.summary == "New summary"
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity
