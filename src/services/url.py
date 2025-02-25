from typing import Dict, Any


def construct_products_search_url(params: Dict[str, Any]):
    base_url = "https://www.mercari.com/search/"
    query_params = []

    if params.get("search_keyword"):
        query_params.append(f"keyword={params['search_keyword'].replace(' ', '%20')}")

    origin = params.get("item_origin", "").lower()
    if origin == "usa":
        query_params.append("countrySources=1")
    elif origin == "japan":
        query_params.append("countrySources=2")

    condition_map = {
        "new": 1,
        "like new": 2,
        "good": 3,
        "fair": 4,
        "poor": 5
    }
    condition = params.get("condition", "").lower()
    if condition in condition_map:
        query_params.append(f"itemConditions={condition_map[condition]}")

    if "price_min" in params and params['price_min'] is not None:
        query_params.append(f"minPrice={params['price_min']}")
    if "price_max" in params and params['price_max'] is not None:
        query_params.append(f"maxPrice={params['price_max']}")

    if params.get("free_shipping"):
        query_params.append("shippingPayerIds=2")

    full_url = f"{base_url}?{'&'.join(query_params)}"

    return full_url
