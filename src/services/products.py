import os
import requests
import concurrent.futures

from typing import Dict
from bs4 import BeautifulSoup

FLARESOLVERR_URL = os.getenv('FLARESOLVERR_URL')


def search_products(products_search_url: str, max_items=10):
    """
    Scrape the given product search URL through flaresolverr.
    Currently, Mercari has CloudFlare protection.
    To bypass, we use flaresolverr here.
    """
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "cmd": "request.get",
        "url": products_search_url,
        "maxTimeout": 10 * 1000
    }

    response = requests.post(FLARESOLVERR_URL, headers=headers, json=data)

    if response.status_code == 200:
        flaresolverr_response = response.json()
        html_content = flaresolverr_response['solution']['response']

    #  parse the html content
    soup = BeautifulSoup(html_content, "html.parser")

    products = []
    product_elements = soup.find_all(attrs={'data-testid': 'ItemContainer'})

    for element in product_elements:
        product_name = element.find('div', attrs={'data-testid': 'ItemName'}).text.strip()
        product_price = element.find('p', attrs={'data-testid': 'ProductThumbItemPrice'}).text.strip()
        product_is_on_sale = element.attrs['data-is-on-sale'] == 'true'
        product_id = element.attrs['data-productid']
        product_url = f'https://www.mercari.com/us/item/{product_id}/?ref=search_results'

        image_tag = element.find('div', attrs={"data-testid": "StyledProductThumb"}).find('img')
        product_image_url = image_tag['src'] if image_tag else None

        products.append({
            "product_name": product_name,
            "product_price": product_price,
            "product_is_on_sale": product_is_on_sale,
            "product_image_url": product_image_url,
            "product_url": product_url
        })

    return products[:max_items]


def extract_categories(soup: BeautifulSoup, product_details: Dict):
    target_element = soup.find('span', attrs={'data-testid': 'ItemDetailsCategory'})

    if target_element is not None:
        product_categories = [a.text for a in target_element.select('[data-testid^="Category_"]')]
        product_details['product_categories'] = ', '.join(product_categories)


def extract_seller_rating(soup: BeautifulSoup, product_details: Dict):
    seller_rating_stars = soup.find(attrs={'data-testid': 'ReviewStarsWrapper'})
    if seller_rating_stars is not None:
        product_details['seller_rating_stars'] = seller_rating_stars.attrs.get('data-stars', '').strip()

    seller_reviews_count = soup.find(attrs={'data-testid': 'SellerRatingCount'})
    if (seller_reviews_count is not None) and (seller_reviews_count.text is not None):
        product_details['seller_reviews_count'] = seller_reviews_count.text.strip() + ' reviews'


def extract_info(soup: BeautifulSoup, product_details: Dict, target_property: str, data_test_id: str):
    target_element = soup.find(attrs={'data-testid': data_test_id})

    if target_element is not None:
        product_details[target_property] = target_element.text.strip()

    return product_details


def retrieve_product_details(product_url: str):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "cmd": "request.get",
        "url": product_url,
        "maxTimeout": 20 * 1000
    }

    response = requests.post(FLARESOLVERR_URL, headers=headers, json=data)

    if response.status_code == 200:
        flaresolverr_response = response.json()
        html_content = flaresolverr_response['solution']['response']
    else:
        print(f'Failed to fetch product details for: {product_url}')
        return {}

    product_details = {}

    soup = BeautifulSoup(html_content, "html.parser")
    spec_element = soup.find(attrs={'data-testid': 'Spec'})

    # The idea is simple -- as we are sure if the element (with our assumed data-testid) will be present all the time,
    # we do best effort strategy, where we inspect it.
    # If the elements are present, then we attach to product details dict.
    extract_info(spec_element, product_details, 'product_update_at', 'ItemDetailExternalUpdated')
    extract_info(spec_element, product_details, 'product_posted_at', 'ItemDetailsPosted')
    extract_info(spec_element, product_details, 'production_condition', 'ItemDetailsCondition')
    extract_info(spec_element, product_details, 'product_brand', 'ItemDetailsBrand')
    extract_info(spec_element, product_details, 'product_description', 'ItemDetailsDescription')

    extract_categories(soup, product_details)
    extract_seller_rating(soup, product_details)

    return product_details


"""
Use this to fetch the products in sequential.
Anyway, flaresolverr has it's own queuing.

def enrich_products(products):
    enriched_products = []

    for product in products:
        details = retrieve_product_details(
            product.get("product_url")
        )

        enriched_products.append({
            **product,
            **details
        })

    return enriched_products
"""


def enrich_products(products):
    """
    Enriches a list of products by retrieving additional details for each product.

    :param products: List of product that we got back from product search
    :return: List of product -- each with more detailed information
    """

    def fetch_details(product):
        print(f'Retrieving product details for: {product.get("product_url")}')
        details = retrieve_product_details(product.get("product_url"))
        return {**product, **details}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        enriched_products = list(executor.map(fetch_details, products))

    return enriched_products
