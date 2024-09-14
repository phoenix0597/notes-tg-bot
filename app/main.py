import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to Notes API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
