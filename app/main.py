from fastapi import FastAPI
from app.api.v1 import cases, terms, teams, students, team_memberships, users, meetings, assignments, checkpoints
from app.db.session import init_db

app = FastAPI(title="ReqRoute API", version="1.0")

app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(terms.router, prefix="/api/v1/terms", tags=["Terms"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(team_memberships.router, prefix="/api/v1/memberships", tags=["Team Memberships"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(meetings.router, prefix="/api/v1/meetings", tags=["Meetings"])
app.include_router(assignments.router, prefix="/api/v1/assignments", tags=["Assignments"])
app.include_router(checkpoints.router, prefix="/api/v1/checkpoints", tags=["Checkpoints"])


@app.on_event("startup")
async def on_startup():
    await init_db()
