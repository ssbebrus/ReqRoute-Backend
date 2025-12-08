from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import selectinload

from app.models import Case
from app.models.meeting import Meeting, MeetingUser
from app.models.meeting_schedule import MeetingSchedule
from app.models.team import Team
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.schemas.meeting_user import MeetingUserCreate
from app.schemas.meeting_schedule import (
    MeetingScheduleCreate,
    MeetingScheduleUpdate,
)
from app.utils.filtering import filter_and_paginate


async def get_meetings_filtered(db: AsyncSession, params: dict):
    return await filter_and_paginate(Meeting, db, params)

async def get_previous_meeting_id(db: AsyncSession, meeting_id: int):
    prev_id = await db.execute(select(Meeting.previous_meeting_id).where(Meeting.id == meeting_id))
    return prev_id.scalar_one_or_none()

async def get_meeting(db: AsyncSession, meeting_id: int):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()

async def link_meeting_user(db: AsyncSession, data: MeetingUserCreate):
    new_link = MeetingUser(**data.model_dump())
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link

async def create_meeting(db: AsyncSession, data: MeetingCreate):
    new_meeting = Meeting(**data.model_dump())
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)
    return  new_meeting

async def update_meeting(db: AsyncSession, meeting_id: int, data: MeetingUpdate):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(meeting, key, value)
    await db.commit()
    await db.refresh(meeting)
    return meeting

async def delete_meeting(db: AsyncSession, meeting_id: int):
    meeting = await get_meeting(db, meeting_id)
    if not meeting:
        return None
    await db.delete(meeting)
    await db.commit()
    return meeting


async def get_team_schedule(db: AsyncSession, team_id: int) -> MeetingSchedule | None:
    result = await db.execute(
        select(MeetingSchedule)
        .where(MeetingSchedule.team_id == team_id)
        .where(MeetingSchedule.active == True)
        .order_by(MeetingSchedule.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_meeting_schedule(db: AsyncSession, data: MeetingScheduleCreate) -> MeetingSchedule:
    team_result = await db.execute(
        select(Team)
        .options(selectinload(Team.case).selectinload(Case.term))
        .where(Team.id == data.team_id)
    )
    team = team_result.scalar_one_or_none()
    if not team:
        raise ValueError(f"Team {data.team_id} not found")

    if not team.case or not team.case.term:
        raise ValueError("Team must have a case with a term")

    term = team.case.term
    if not term.end_date:
        raise ValueError("Term must have an end_date")

    existing_schedules = await db.execute(
        select(MeetingSchedule)
        .where(MeetingSchedule.team_id == data.team_id)
        .where(MeetingSchedule.active == True)
    )
    for schedule in existing_schedules.scalars():
        schedule.active = False

    schedule = MeetingSchedule(**data.model_dump())
    db.add(schedule)
    await db.flush()

    meetings = _generate_meetings_from_schedule(
        schedule, term.end_date, team_id=data.team_id
    )

    db.add_all(meetings)
    await db.flush()

    for i in range(1, len(meetings)):
        meetings[i].previous_meeting_id = meetings[i - 1].id

    await db.commit()
    await db.refresh(schedule)
    return schedule


def _generate_meetings_from_schedule(schedule: MeetingSchedule, end_date: date, team_id: int) -> list[Meeting]:
    meetings = []
    current_date = schedule.start_date

    days_ahead = schedule.day_of_week - current_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_meeting_date = current_date + timedelta(days=days_ahead)
    current_datetime = datetime.combine(first_meeting_date, schedule.time)

    while current_datetime.date() <= end_date:
        meeting = Meeting(
            team_id=team_id,
            schedule_id=schedule.id,
            previous_meeting_id=None,
            date_time=current_datetime,
            summary=None,
            recording_link=None,
        )
        meetings.append(meeting)

        current_datetime += timedelta(weeks=schedule.interval_weeks)

    for i in range(1, len(meetings)):
        meetings[i].previous_meeting_id = None

    return meetings


async def update_meeting_schedule(db: AsyncSession, schedule_id: int, data: MeetingScheduleUpdate) -> MeetingSchedule | None:
    schedule_result = await db.execute(
        select(MeetingSchedule)
        .options(selectinload(MeetingSchedule.team).selectinload(Team.case).selectinload(Case.term))
        .where(MeetingSchedule.id == schedule_id)
    )
    schedule = schedule_result.scalar_one_or_none()
    if not schedule:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return schedule

    now = datetime.now()
    future_meetings_result = await db.execute(
        select(Meeting)
        .where(Meeting.schedule_id == schedule_id)
        .where(Meeting.date_time > now)
    )
    for meeting in future_meetings_result.scalars():
        await db.delete(meeting)

    for key, value in update_data.items():
        setattr(schedule, key, value)

    await db.flush()

    if schedule.active:
        team = schedule.team
        if team.case and team.case.term and team.case.term.end_date:
            start_date = (
                update_data.get("start_date")
                if "start_date" in update_data
                else schedule.start_date
            )
            day_of_week = (
                update_data.get("day_of_week")
                if "day_of_week" in update_data
                else schedule.day_of_week
            )
            meeting_time = (
                update_data.get("time")
                if "time" in update_data
                else schedule.time
            )
            interval_weeks = (
                update_data.get("interval_weeks")
                if "interval_weeks" in update_data
                else schedule.interval_weeks
            )

            temp_schedule = MeetingSchedule(
                team_id=schedule.team_id,
                start_date=start_date,
                day_of_week=day_of_week,
                time=meeting_time,
                interval_weeks=interval_weeks,
            )

            effective_start = max(start_date, now.date())
            meetings = _generate_meetings_from_schedule(
                temp_schedule, team.case.term.end_date, team_id=schedule.team_id
            )
            future_meetings = [
                m for m in meetings if m.date_time > now and m.date_time.date() >= effective_start
            ]

            for m in future_meetings:
                m.schedule_id = schedule.id

            db.add_all(future_meetings)
            await db.flush()

            if future_meetings:
                last_existing = await db.execute(
                    select(Meeting)
                    .where(Meeting.schedule_id == schedule_id)
                    .where(Meeting.date_time <= now)
                    .order_by(Meeting.date_time.desc())
                    .limit(1)
                )
                last_meeting = last_existing.scalar_one_or_none()

                previous = last_meeting
                for meeting in future_meetings:
                    meeting.previous_meeting_id = previous.id if previous else None
                    previous = meeting

    await db.commit()
    await db.refresh(schedule)
    return schedule