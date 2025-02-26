from dotenv import load_dotenv
load_dotenv()

import os
import json

from openai import OpenAI
from typing import List, Literal
from pydantic import BaseModel, Field

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .services import (
    extract_filters,
    construct_products_search_url,
    search_products,
    recommend_products
)

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
def generate_search_completion(request: SearchCompletionRequest):
    response = generate_streamed_response(request.messages)

    return StreamingResponse(
        response,
        media_type='text/plain'
    )


def generate_streamed_response(messages: List[Message]):
    """
    As the downstream client is NextJS / TypeScript,
    we will use camelCase for JSON keys
    """

    yield json.dumps({
        "blockType": "status_update",
        "status": "extracting_filters",
        "message": "Analysing user query, extracting search keywords and filters."
    }) + '\n'


    parsed_result, error = extract_filters(openai_client, messages)

    yield json.dumps({
        "blockType": "status_update",
        "status": "filters_extraction_done",
        "message": "Has identified & prepared the following filters based on user query.",
        "filters": dict(parsed_result)
    }) + '\n'

    products_search_url = construct_products_search_url(parsed_result)

    yield json.dumps({
        "blockType": "status_update",
        "status": "scraping_products",
        "message": "Searching relevant products",
        "url": products_search_url
    }) + '\n'

    products = search_products(products_search_url)

    yield json.dumps({
        "blockType": "status_update",
        "status": "products_scraped",
        "message": f"Got {len(products)} products from Mercari. Analysing most relevant products...",
        "products": products
    }) + '\n'

    # TODO:: would be great if we can do conversation support.
    # But, this is not as dire as conversation support in filter extractions
    user_query = messages[-1].content

    stream = recommend_products(openai_client, products, user_query)
    for token in stream:
        yield json.dumps({
            "blockType": "completion_response",
            "content": token
        }) + '\n'
