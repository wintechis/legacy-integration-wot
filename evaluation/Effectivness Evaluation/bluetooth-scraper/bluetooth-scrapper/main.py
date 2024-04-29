import asyncio
import json
import os
from playwright.async_api import async_playwright
import aiofiles
import requests



def fetch_json_for_listing_id(listing_id):
    url = f"https://platformapi.bluetooth.com/api/Platform/ListingDetails/{listing_id}"

    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        return data
    
    return None

async def save_json_content(listing_id, content):
    filename = f'../data/device_details/{listing_id}.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    async with aiofiles.open(filename, 'w') as file:
        await file.write(json.dumps(content, indent=4))

def get_existing_ids():
    folder_path = '../data/device_details'
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    return [f.split('.')[0] for f in files]

async def process_json_file(filepath):
    async with aiofiles.open(filepath, 'r') as file:
        content = await file.read()
        data = json.loads(content)
        existing_ids = get_existing_ids()
        print(existing_ids)
        for item in data:
            listing_id = item.get('ListingId')
            if listing_id:
                if str(listing_id) in existing_ids:
                    print(f'Already found device for listing id: {listing_id}')
                    continue
                json_content = fetch_json_for_listing_id(listing_id)
                print(f'Found device for listing id: {listing_id}')
                await save_json_content(listing_id, json_content)

async def main():
    json_folder_path = '../data/bluetooth_devices'
    json_files = [f for f in os.listdir(json_folder_path) if f.endswith('.json')]
    for json_file in json_files:
        await process_json_file(os.path.join(json_folder_path, json_file))

asyncio.run(main())
