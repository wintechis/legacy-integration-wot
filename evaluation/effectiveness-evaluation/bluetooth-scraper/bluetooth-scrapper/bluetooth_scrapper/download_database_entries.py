import json

import requests

# The URL is constructed from the scheme, host, and filename
url = "https://platformapi.bluetooth.com/api/platform/Listings/Search"


# Request payload
payload = {
    "searchString": None,
    "searchQualificationsAndDesigns": True,
    "searchDeclarationOnly": True,
    "searchEndProductList": False,
    "searchPRDProductList": True,
    "searchMyCompany": False,
    "productTypeId": 0,
    "icsItem": "",
    "specName": 0,
    "bqaApprovalStatusId": -1,
    "bqaLockStatusId": -1,
    "listingDateEarliest": "2023-03-05",
    "listingDateLatest": "2024-03-05",
    "userId": 0,
    "memberId": None,
    "layers": [],
    "maxResults": 50000,
}


year_range = 2025 - 1999

for i in range(year_range):
    earliest_date = f"{2025 - i}-01-01"
    latest_date = f"{2025 - i}-12-31"
    payload["listingDateEarliest"] = earliest_date
    payload["listingDateLatest"] = latest_date

    # Make the POST request
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response content
        print(f"Response from server for {latest_date} to {earliest_date}:")
        print(len(response.json()))
        dump = json.dumps(response.json(), indent=4)
        # print(dump)
        with open(
            f"../../data/bluetooth_devices/{earliest_date}_{latest_date}.json", "w"
        ) as f:
            f.write(dump)
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
