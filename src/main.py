import os
import asyncio

from typing import List, Literal

from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/")
def health_check():
    return {"message": "Mercari Advanced Search - AI Agent is running fine!"}


class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(..., min_length=1,
                         description='The content of the message. Either user query or system response.')


class SearchCompletionRequest(BaseModel):
    messages: List[Message]


@app.post('/generate-search-completion')
async def generate_search_completion(request: SearchCompletionRequest):
    response = generate_streamed_response(request.messages)

    return StreamingResponse(
        response,
        media_type='text/plain'
    )


async def generate_streamed_response(messages: List[Message]):
    await asyncio.sleep(3)  # Simulating delay
    yield "Starting response...\n"

    for message in messages:
        chunk = f"Role: {message.role} - Content: {message.content}\n"
        yield chunk
        await asyncio.sleep(1)  # Simulate processing delay

    yield "End of stream.\n"
