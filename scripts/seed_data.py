import asyncio
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal, engine, Base
from app.models.assignment import Assignment
from app.models.case import Case
from app.models.checkpoint import Checkpoint
from app.models.meeting import Meeting
from app.models.student import Student
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.term import Term, SeasonEnum
from app.models.user import User


def _make_terms():
    return [
        Term(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 1, 31),
            year=2024,
            season=SeasonEnum.autumn,
        ),
        Term(
            start_date=date(2025, 2, 1),
            end_date=date(2025, 6, 30),
            year=2025,
            season=SeasonEnum.spring,
        ),
    ]


def _make_users():
    return [
        User(
            full_name="Alice Owner",
            email="alice@example.com",
            password="demo",
        ),
        User(
            full_name="Bob Reviewer",
            email="bob@example.com",
            password="demo",
        ),
        User(
            full_name="Charlie Mentor",
            email="charlie@example.com",
            password="demo",
        ),
    ]


def _make_cases(term_a, term_b, users):
    return [
        Case(
            term=term_a,
            user=users[0],
            title="AI Research Project",
            description="NLP case",
        ),
        Case(
            term=term_a,
            user=users[1],
            title="Data Warehouse Revamp",
            description="ETL case",
        ),
        Case(
            term=term_b,
            user=users[2],
            title="Mobile App Launch",
            description="React Native",
        ),
    ]


def _make_teams(cases):
    return [
        Team(
            title="Team Alpha",
            case=cases[0],
            workspace_link="https://example.com/ws/alpha",
            final_mark=0,
        ),
        Team(
            title="Team Beta",
            case=cases[0],
            workspace_link="https://example.com/ws/beta",
            final_mark=0,
        ),
        Team(
            title="Team Gamma",
            case=cases[1],
            workspace_link="https://example.com/ws/gamma",
            final_mark=0,
        ),
        Team(
            title="Team Delta",
            case=cases[2],
            workspace_link="https://example.com/ws/delta",
            final_mark=0,
        ),
    ]


def _make_students():
    return [
        Student(full_name="Student One"),
        Student(full_name="Student Two"),
        Student(full_name="Student Three"),
        Student(full_name="Student Four"),
        Student(full_name="Student Five"),
    ]


def _make_memberships(students, teams):
    return [
        TeamMembership(
            student=students[0],
            team=teams[0],
            role="Lead",
            group="A-1",
        ),
        TeamMembership(
            student=students[1],
            team=teams[0],
            role="Analyst",
            group="A-1",
        ),
        TeamMembership(
            student=students[2],
            team=teams[1],
            role="Dev",
            group="B-2",
        ),
        TeamMembership(
            student=students[3],
            team=teams[2],
            role="PM",
            group="C-3",
        ),
        TeamMembership(
            student=students[4],
            team=teams[3],
            role="QA",
            group="D-4",
        ),
    ]


def _make_meetings(teams):
    now = datetime.now(tz=timezone.utc)
    meetings = []
    for team in teams:
        m1 = Meeting(
            team=team,
            previous_meeting_id=None,
            recording_link=None,
            date_time=now,
            summary=f"{team.title} Kick-off",
        )
        m2 = Meeting(
            team=team,
            previous_meeting_id=None,
            recording_link=None,
            date_time=now.replace(hour=14),
            summary=f"{team.title} Checkpoint",
        )
        m3 = Meeting(
            team=team,
            previous_meeting_id=None,
            recording_link=None,
            date_time=now.replace(hour=16),
            summary=f"{team.title} Wrap-up",
        )
        meetings.extend([m1, m2, m3])
    return meetings


def _make_assignments(meetings):
    assignments = []
    for m in meetings:
        assignments.append(
            Assignment(
                meeting=m,
                text=f"Prepare for {m.summary}",
                completed=False,
            )
        )
        assignments.append(
            Assignment(
                meeting=m,
                text=f"Follow-up from {m.summary}",
                completed=None,
            )
        )
    return assignments


def _make_checkpoints(teams):
    checkpoints = []
    for i, team in enumerate(teams, start=1):
        checkpoints.append(
            Checkpoint(
                team=team,
                number=1,
                date=date(2024, 9, 20),
                project_state="In progress",
                mark=5 + (i % 5),
                video_link=None,
                presentation_link=None,
                university_mark=None,
                university_comment=None,
            )
        )
    return checkpoints


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing = await session.execute(select(User).limit(1))
        if existing.scalars().first():
            print("Seed data already present; skipping.")
            return

        terms = _make_terms()
        users = _make_users()
        cases = _make_cases(terms[0], terms[1], users)
        teams = _make_teams(cases)
        students = _make_students()
        memberships = _make_memberships(students, teams)
        meetings = _make_meetings(teams)
        assignments = _make_assignments(meetings)
        checkpoints = _make_checkpoints(teams)

        session.add_all(
            terms
            + users
            + cases
            + teams
            + students
            + memberships
            + meetings
            + assignments
            + checkpoints
        )

        await session.flush()
        for i in range(0, len(meetings), 3):
            first, second, third = meetings[i:i+3]
            second.previous_meeting_id = first.id
            third.previous_meeting_id = second.id

        await session.commit()
        print(
            "Seeded "
            f"{len(users)} users, "
            f"{len(terms)} terms, "
            f"{len(cases)} cases, "
            f"{len(teams)} teams, "
            f"{len(students)} students, "
            f"{len(meetings)} meetings, "
            f"{len(assignments)} assignments, "
            f"{len(checkpoints)} checkpoints."
        )


def run():
    asyncio.run(seed())


if __name__ == "__main__":
    run()
