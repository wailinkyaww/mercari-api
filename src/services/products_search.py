import os
import requests

from bs4 import BeautifulSoup

FLARESOLVERR_URL = os.getenv('FLARESOLVERR_URL')


def search_products(product_search_url: str, max_items=10):
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
        "url": product_search_url,
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

        image_tag = element.find('div', attrs={"data-testid": "StyledProductThumb"}).find('img')
        product_image_url = image_tag['src'] if image_tag else None

        products.append({
            "product_name": product_name,
            "product_price": product_price,
            "product_is_on_sale": product_is_on_sale,
            "product_image_url": product_image_url
        })

    return products[:max_items]
