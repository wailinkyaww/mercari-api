import json

from openai import OpenAI
from typing import List

PRODUCT_RECOMMENDATION_PROMPT = """
You are an expert at understanding user requests for online marketplaces, specifically for Mercari Japan. 

You will be provided with the input from user and relevant product search results those are tailored to the user query.

Your job is to pick top 3 most relevant products out of the provided product search results.

You should also provide reasoning why each choice is relevant to user's request.

**User Query**
{user_query}

**Relevant Products Found**
{products}

Now provide the output in presentable markdown format to user.
"""


def recommend_products(openai_client: OpenAI, products: List, user_query: str):
    prompt = PRODUCT_RECOMMENDATION_PROMPT.format(
        user_query=user_query,
        products=json.dumps(obj=products, indent=2)
    )

    stream = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4-turbo",
        stream=True
    )

    for chunk in stream:
        token = chunk.choices[0].delta.content

        if (token is not None) or (token != ""):
            yield token
