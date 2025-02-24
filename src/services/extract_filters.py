import json

from openai import OpenAI

EXTRACT_FILTERS_PROMPT = """
You are an expert at understanding user requests for online marketplaces, specifically for Mercari Japan. 

You will be provided with the input from user.

Always extract the following information in JSON format:
1. **search_keyword**: The main item(s) the user wants to buy.
2. **item_origin**: One of the following: "Any", "USA", or "Japan". (If not mentioned, default to "Any").
3. **condition**: One of these values - "new", "like new", "good", "fair", "poor". (If not mentioned, set to null).
4. **price_min**: Minimum price if specified, otherwise null.
5. **price_max**: Maximum price if specified, otherwise null.
6. **free_shipping**: true or false. (If not mentioned, set to false).

Example Output:
```json
{
"search_keyword": "leather shorts",
  "item_origin": "Japan",
  "condition": "like new",
  "price_min": 1000,
  "price_max": 5000,
  "free_shipping": true
}

Only respond with the valid JSON format for the extracted information.
"""


def extract_filters(openai_client: OpenAI, messages):
    """
    messages should be an array of message each with
     role - either user or assistant
     content - message content

    The function will extract the filters to perform the product search on Mercari.
    The function will also look at the conversation history.

    For example:
    Input coming from client side:
        user: I'm looking for a gym bag from Japan.
        assistant: <suggests something>
        user: I would prefer like new, under 5000 yen, and free shipping.
    """

    response = openai_client.chat.completions.create(
        messages=[{"role": "system", "content": EXTRACT_FILTERS_PROMPT}] + messages,
        model="gpt-4-turbo"
    )

    llm_response = response.choices[0].message.content

    try:
        # clean if the model produce the markdown tagging for JSON
        llm_response = llm_response.replace('```json', '')
        llm_response = llm_response.replace('```', '')
        llm_response = llm_response.strip()

        parsed_result = json.loads(llm_response)
        return parsed_result, None
    except json.JSONDecodeError:
        error = {
            "message": "Sorry, we couldn't extract the relevant filters from your query. Please try again."
        }
        return None, error
