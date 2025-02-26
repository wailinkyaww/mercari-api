import json

from openai import OpenAI
from typing import List

PRODUCT_RECOMMENDATION_PROMPT = """
You are an expert at understanding user requests for online marketplaces, specifically for Mercari Japan. 

You will be provided with the input from user and relevant product search results those are tailored to the user query.

Each product will include 
- name
- description
- price
- sale status
- categories
- seller ratings (stars & review counts)

Note that these fields can be missing as well.

Your job is to pick top 3 most relevant products out of the provided product search results.
You should also provide reasoning why each choice is relevant to user's request.

Use your best ability to pick most relevant products and provide recommendation to user.
Provide clear and concise reasoning for each recommendation.

**User Query**
{user_query}

**Relevant Products Found**
{products}


Here is the outline for your response.

#### 1. Product name
- **<Property 1>:** <value>
- **<Property 2>:** <value>
- ...
- **Reasoning:** Provide a reasoning description on why you recommend this product.
<Markdown Image>
<View Product on Mercari - use product url>

#### 2. Product name
- **<Property 1>:** <value>
- **<Property 2>:** <value>
- ...
- **Reasoning:** Provide a reasoning description on why you recommend this product.
<Markdown Image>
<View Product on Mercari - use product url>

Answer from the point of view that you are talking to user.
Do not mention anything about the provided list.
Do not include any filler words.

Make sure you provide all the useful information in each recommendation block.
Now generate the recommendation output up to 3 products in presentable markdown format to user.
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
