import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

from app.api import auth, note


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(note.router)


@app.get("/", tags=["Welcome endpoint"])
async def root():
    return {"message": "Welcome to Notes API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
