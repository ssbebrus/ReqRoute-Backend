from fastapi import FastAPI
from app.api.v1 import cases, terms, teams
from app.db.session import init_db

app = FastAPI(title="ReqRoute API", version="1.0")

app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(terms.router, prefix="/api/v1/terms", tags=["Terms"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])


@app.on_event("startup")
async def on_startup():
    await init_db()
