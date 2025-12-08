import datetime
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.meeting import Meeting, MeetingUser
from app.models.meeting_schedule import MeetingSchedule
from app.models.team import Team
from app.models.case import Case
from app.models.term import Term, SeasonEnum
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.schemas.meeting_user import MeetingUserCreate
from app.schemas.meeting_schedule import (
    MeetingScheduleCreate,
    MeetingScheduleUpdate,
)
from app.services import meeting_service


@pytest.mark.asyncio
async def test_get_previous_meeting_id_uses_scalar(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([7])

    previous_id = await meeting_service.get_previous_meeting_id(
        mock_session, meeting_id=10
    )

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
    monkeypatch.setattr(
        meeting_service, "get_meeting", AsyncMock(return_value=None)
    )

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
    monkeypatch.setattr(
        meeting_service, "get_meeting", AsyncMock(return_value=entity)
    )

    meeting_id = entity.id if hasattr(entity, "id") else 1
    deleted = await meeting_service.delete_meeting(
        mock_session, meeting_id=meeting_id
    )

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_meeting_returns_scalar_one_or_none(
    mock_session, result_stub
):
    stored = Meeting(
        team_id=1,
        previous_meeting_id=None,
        recording_link=None,
        date_time=datetime.datetime.now(datetime.timezone.utc),
        summary="Test",
    )
    mock_session.execute.return_value = result_stub([stored])

    meeting = await meeting_service.get_meeting(mock_session, meeting_id=1)

    assert meeting == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_meeting_returns_none_when_not_found(
    mock_session, result_stub
):
    mock_session.execute.return_value = result_stub([])

    meeting = await meeting_service.get_meeting(
        mock_session, meeting_id=999
    )

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
    monkeypatch.setattr(
        meeting_service, "get_meeting", AsyncMock(return_value=entity)
    )
    patch = MeetingUpdate(summary="New summary")

    updated = await meeting_service.update_meeting(
        mock_session, meeting_id=1, data=patch
    )

    assert updated is entity
    assert updated.summary == "New summary"
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity


@pytest.mark.asyncio
async def test_get_team_schedule_returns_active_schedule(
    mock_session, result_stub
):
    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
        active=True,
    )
    mock_session.execute.return_value = result_stub([schedule])

    result = await meeting_service.get_team_schedule(
        mock_session, team_id=1
    )

    assert result == schedule
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_team_schedule_returns_none_when_no_active_schedule(
    mock_session, result_stub
):
    mock_session.execute.return_value = result_stub([])

    result = await meeting_service.get_team_schedule(
        mock_session, team_id=1
    )

    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_meeting_schedule_generates_meetings(monkeypatch, mock_session):
    term = Term(
        start_date=date(2025, 9, 1),
        end_date=date(2025, 12, 31),
        year=2024,
        season=SeasonEnum.autumn,
    )
    case = Case(term_id=1, user_id=1, title="Test Case", description=None)
    case.term = term

    team = Team(
        id=1,
        title="Test Team",
        case_id=1,
        workspace_link=None,
        final_mark=0,
    )
    team.case = case

    team_result = MagicMock()
    team_result.scalar_one_or_none.return_value = team

    existing_schedules_result = MagicMock()
    existing_schedules_result.scalars.return_value = []

    def execute_side_effect(query):
        text = str(query)
        if "FROM teams" in text or "Team" in text:
            return team_result
        if "FROM meeting_schedules" in text or "MeetingSchedule" in text:
            return existing_schedules_result
        return MagicMock()

    mock_session.execute = AsyncMock(side_effect=execute_side_effect)

    payload = MeetingScheduleCreate(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
    )

    schedule = await meeting_service.create_meeting_schedule(
        mock_session, payload
    )

    assert isinstance(schedule, MeetingSchedule)
    assert schedule.team_id == 1
    assert mock_session.flush.await_count >= 1
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_create_meeting_schedule_raises_when_team_not_found(
    monkeypatch, mock_session
):
    team_result = MagicMock()
    team_result.scalar_one_or_none.return_value = None

    mock_session.execute = AsyncMock(return_value=team_result)

    payload = MeetingScheduleCreate(
        team_id=999,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
    )

    with pytest.raises(ValueError, match="Team 999 not found"):
        await meeting_service.create_meeting_schedule(
            mock_session, payload
        )


@pytest.mark.asyncio
async def test_create_meeting_schedule_raises_when_no_case_or_term(
    monkeypatch, mock_session
):
    team = Team(
        title="Test Team", case_id=1, workspace_link=None, final_mark=0
    )
    team.case = None

    team_result = MagicMock()
    team_result.scalar_one_or_none.return_value = team

    mock_session.execute = AsyncMock(return_value=team_result)

    payload = MeetingScheduleCreate(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
    )

    with pytest.raises(ValueError, match="Team must have a case with a term"):
        await meeting_service.create_meeting_schedule(
            mock_session, payload
        )


@pytest.mark.asyncio
async def test_create_meeting_schedule_deactivates_existing_schedules(
    monkeypatch, mock_session
):
    term = Term(
        start_date=date(2024, 9, 1),
        end_date=date(2024, 10, 31),
        year=2024,
        season=SeasonEnum.autumn,
    )
    case = Case(term_id=1, user_id=1, title="Test Case", description=None)
    case.term = term
    team = Team(
        title="Test Team", case_id=1, workspace_link=None, final_mark=0
    )
    team.case = case

    existing_schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 8, 1),
        day_of_week=0,
        time=time(10, 0),
        interval_weeks=1,
        active=True,
    )

    team_result = MagicMock()
    team_result.scalar_one_or_none.return_value = team

    existing_schedules_result = MagicMock()
    existing_schedules_result.scalars.return_value = [existing_schedule]

    call_count = 0

    def execute_side_effect(query):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return team_result
        elif call_count == 2:
            return existing_schedules_result
        return MagicMock()

    mock_session.execute = AsyncMock(side_effect=execute_side_effect)

    payload = MeetingScheduleCreate(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
    )

    await meeting_service.create_meeting_schedule(
        mock_session, payload
    )

    assert existing_schedule.active is False


def test_generate_meetings_from_schedule_weekly():
    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
    )
    schedule.id = 1
    end_date = date(2024, 9, 15)

    meetings = meeting_service._generate_meetings_from_schedule(
        schedule, end_date, team_id=1
    )

    assert len(meetings) == 2
    assert meetings[0].date_time.date() == date(2024, 9, 2)
    assert meetings[1].date_time.date() == date(2024, 9, 9)
    assert all(m.team_id == 1 for m in meetings)
    assert all(m.schedule_id == 1 for m in meetings)
    assert all(m.date_time.time() == time(12, 0) for m in meetings)


def test_generate_meetings_from_schedule_biweekly():
    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=2,
        time=time(14, 30),
        interval_weeks=2,
    )
    schedule.id = 1
    end_date = date(2024, 9, 20)

    meetings = meeting_service._generate_meetings_from_schedule(
        schedule, end_date, team_id=1
    )

    assert len(meetings) == 2
    assert meetings[0].date_time.date() == date(2024, 9, 4)
    assert meetings[1].date_time.date() == date(2024, 9, 18)
    assert all(m.team_id == 1 for m in meetings)
    assert all(m.schedule_id == 1 for m in meetings)


@pytest.mark.asyncio
async def test_update_meeting_schedule_returns_none_when_not_found(
    mock_session, result_stub
):
    mock_session.execute.return_value = result_stub([])

    update_data = MeetingScheduleUpdate(day_of_week=1)

    result = await meeting_service.update_meeting_schedule(
        mock_session, schedule_id=999, data=update_data
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_meeting_schedule_updates_fields(
    monkeypatch, mock_session
):
    term = Term(
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 31),
        year=2024,
        season=SeasonEnum.autumn,
    )
    case = Case(term_id=1, user_id=1, title="Test Case", description=None)
    case.term = term
    team = Team(
        title="Test Team", case_id=1, workspace_link=None, final_mark=0
    )
    team.case = case

    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
        active=True,
    )
    schedule.id = 1
    schedule.team = team

    schedule_result = MagicMock()
    schedule_result.scalar_one_or_none.return_value = schedule

    future_meetings_result = MagicMock()
    future_meetings_result.scalars.return_value = []

    call_count = 0

    def execute_side_effect(query):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return schedule_result
        elif call_count == 2:
            return future_meetings_result
        return MagicMock()

    mock_session.execute = AsyncMock(side_effect=execute_side_effect)

    update_data = MeetingScheduleUpdate(day_of_week=2, time=time(14, 0))

    updated = await meeting_service.update_meeting_schedule(
        mock_session, schedule_id=1, data=update_data
    )

    assert updated is schedule
    assert schedule.day_of_week == 2
    assert schedule.time == time(14, 0)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_update_meeting_schedule_deletes_future_meetings(
    monkeypatch, mock_session
):
    term = Term(
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 31),
        year=2024,
        season=SeasonEnum.autumn,
    )
    case = Case(term_id=1, user_id=1, title="Test Case", description=None)
    case.term = term
    team = Team(
        title="Test Team", case_id=1, workspace_link=None, final_mark=0
    )
    team.case = case

    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
        active=True,
    )
    schedule.id = 1
    schedule.team = team

    future_meeting1 = Meeting(
        team_id=1,
        schedule_id=1,
        date_time=datetime.datetime(2024, 10, 1, 12, 0),
    )
    future_meeting2 = Meeting(
        team_id=1,
        schedule_id=1,
        date_time=datetime.datetime(2024, 10, 8, 12, 0),
    )

    schedule_result = MagicMock()
    schedule_result.scalar_one_or_none.return_value = schedule

    future_meetings_result = MagicMock()
    future_meetings_result.scalars.return_value = [
        future_meeting1,
        future_meeting2,
    ]

    call_count = 0

    def execute_side_effect(query):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return schedule_result
        elif call_count == 2:
            return future_meetings_result
        return MagicMock()

    mock_session.execute = AsyncMock(side_effect=execute_side_effect)

    update_data = MeetingScheduleUpdate(day_of_week=1)

    await meeting_service.update_meeting_schedule(
        mock_session, schedule_id=1, data=update_data
    )

    assert mock_session.delete.await_count == 2


@pytest.mark.asyncio
async def test_update_meeting_schedule_no_update_when_empty_data(
    monkeypatch, mock_session
):
    schedule = MeetingSchedule(
        team_id=1,
        start_date=date(2024, 9, 1),
        day_of_week=0,
        time=time(12, 0),
        interval_weeks=1,
        active=True,
    )
    schedule.id = 1

    schedule_result = MagicMock()
    schedule_result.scalar_one_or_none.return_value = schedule

    mock_session.execute = AsyncMock(return_value=schedule_result)

    update_data = MeetingScheduleUpdate()

    result = await meeting_service.update_meeting_schedule(
        mock_session, schedule_id=1, data=update_data
    )

    assert result is schedule
    assert mock_session.commit.await_count == 0
