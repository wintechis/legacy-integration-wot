import json

import requests
from bs4 import BeautifulSoup

user_agent = {"User-agent": "Mozilla/5.0"}

products = []
for page in range(1, 131):
    uri = f"https://csa-iot.org/csa-iot_products/page/{page}/?p_keywords&p_type%5B0%5D=14&p_program_type%5B0%5D=966&p_certificate&p_family"
    if page % 10 == 0:
        print(f"Page {page} of 130")
        product_string = json.dumps(products)
        with open("products.json", "w") as f:
            f.write(product_string)
    response = requests.get(uri, headers=user_agent)
    html_doc = response.text
    # print(response.text)

    # Parse the HTML content
    soup = BeautifulSoup(html_doc, "lxml")

    # Find all 'a' tags
    tags = soup.find_all("a")

    # Extract 'href' attributes
    hrefs = [tag.get("href") for tag in tags]

    for href in hrefs:
        if href is not None:
            if "https://csa-iot.org/csa_product/" in href:
                products.append(href)


print(products)

product_string = json.dumps(products)
with open("products.json", "w") as f:
    f.write(product_string)
