from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException

from . import store
from .models import Session, SessionRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.initialize()
    yield


app = FastAPI(title="Cloud Coding Agent", lifespan=lifespan)


@app.post("/sessions", status_code=201)
def create_session(request: SessionRequest) -> Session:
    session = Session(id=uuid4(), **request.model_dump())
    store.save(session)
    return session


@app.get("/sessions/{session_id}")
def get_session(session_id: UUID) -> Session:
    session = store.find(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
