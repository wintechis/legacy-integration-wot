import requests
from bs4 import BeautifulSoup
import json

user_agent = {'User-agent': 'Mozilla/5.0'}

with open('../../data/products.json', 'r') as f:
    products = json.loads(f.read())  

res = {}
for num, product in enumerate(products):
    response = requests.get(product, headers=user_agent)
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract product details based on their HTML structure
    # NOTE: You need to inspect the HTML and adjust these selectors
    product_stats = soup.find('div', class_='entry-product-details')

    # Find all 'li' elements with the class 'item'
    items = product_stats.find_all('li', class_='item')

    # Extract labels and values
    product_details = {}
    for item in items:
        label = item.find('span', class_='label').text.strip()
        # For values, we check if there's an 'a' tag (link), if so, extract the href attribute, otherwise get the text
        value_container = item.find('span', class_='value')
        if value_container.find('a'):  # If there's a link in the value
            value = value_container.find('a')['href'].strip()
        else:
            value = value_container.text.strip()
        
        product_details[label] = value
    
    res[product] = product_details
    
    
    if num % 10 == 0:  
        print(f"Device {num} of {len(products)}")
        product_string = json.dumps(res, indent=4)
        with open('../../data/products_detailed.json', 'w') as f:
            f.write(product_string)     


print(f"Device {num} of {len(products)}")
product_string = json.dumps(res, indent=4)
with open('../../data/products_detailed.json', 'w') as f:
    f.write(product_string)     


print(res)

    
    
    


