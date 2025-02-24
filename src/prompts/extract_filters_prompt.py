EXTRACT_FILTERS_PROMPT_TEMPLATE = """
You are an expert at understanding user requests for online marketplaces, specifically for Mercari Japan. 

Given the user's input, extract the following information in JSON format:

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

User input: "{user_query}"

Provide only the JSON output.
"""
