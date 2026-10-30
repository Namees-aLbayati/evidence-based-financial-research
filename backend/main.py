"""Run from the project folder: python -m uvicorn backend.main:app --reload"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

load_dotenv(Path(__file__).resolve().parent.parent / '.env', override=False)
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)

    @field_validator('question')
    @classmethod
    def strip_question(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Enter a question.')
        return value


class AnswerResponse(BaseModel):
    question: str
    status: Literal['answered', 'partial', 'insufficient_evidence']
    answer: str
    sources: list[dict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    coverage_notes: list[str] = Field(default_factory=list)
    citation_labels_valid: bool
    cache_hit: bool


@asynccontextmanager
async def lifespan(app):
    # Import once at startup; no notebook execution or paid API calls here.
    if not hasattr(app.state, "answer_question"):
        from backend.pipeline import final_inference
        app.state.answer_question = final_inference
    yield


app = FastAPI(title='Financial Research Assistant', lifespan=lifespan)
origins = [value.strip() for value in os.getenv(
    'FRONTEND_ORIGINS', 'http://localhost:3000,http://localhost:5173'
).split(',') if value.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])


UI_DIRECTORY = Path(__file__).resolve().parent / 'static' / 'react'
app.mount('/ui', StaticFiles(directory=UI_DIRECTORY, check_dir=False), name='react-ui')


@app.get('/', response_class=FileResponse, include_in_schema=False)
def home():
    return FileResponse(UI_DIRECTORY / 'index.html')


@app.get('/health')
def health():
    return {'status': 'ready'}


@app.post('/ask', response_model=AnswerResponse)
def ask(payload: QuestionRequest, request: Request):
    try:
        return request.app.state.answer_question(payload.question)
    except Exception as error:
        # Do not expose upstream error bodies, credentials, or internal paths.
        logger.error('Answer request failed (%s)', type(error).__name__)
        raise HTTPException(status_code=503, detail=(
            'Unable to answer right now. Check backend API access and retry.'
        )) from None
