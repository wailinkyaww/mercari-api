import json
import os

from typing import List, Literal

from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .services import extract_filters, construct_product_search_url

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
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
    """
    As the downstream client is NextJS / TypeScript,
    we will use camelCase for JSON keys
    """

    yield json.dumps({
        "blockType": "status_update",
        "status": "query_analysis",
        "message": "Analysing user query - what to buy on Mercari"
    }) + '\n'

    yield json.dumps({
        "blockType": "status_update",
        "status": "extracting_filters",
        "message": "Extracting search keywords and filters."
    }) + '\n'

    parsed_result, error = extract_filters(openai_client, messages)

    yield json.dumps({
        "blockType": "status_update",
        "status": "filters_extraction_done",
        "message": "Has identified & prepared the following filters based on your query.",
        "filters": dict(parsed_result)
    }) + '\n'

    product_search_url = construct_product_search_url(parsed_result)

    print(parsed_result)
    print(product_search_url)
