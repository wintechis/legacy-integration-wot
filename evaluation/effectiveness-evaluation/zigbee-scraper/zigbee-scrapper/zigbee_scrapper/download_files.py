import requests
import zipfile
import os
import shutil
import json
import rarfile
import py7zr

user_agent = {'User-agent': 'Mozilla/5.0'}

with open('products_detailed.json', 'r') as f:
    products = json.loads(f.read())  

    for _, product in products.items():   
        
        if "Certificate ID" not in product:
            print(f"No certificate ID found for {_}")
            continue
        if "Compliance Document" not in product:
            print(f"No Compliance Document found for {_}")
            continue
        device_name = product["Certificate ID"]
        # URL of the ZIP file
        
        # Checks if the device name already exists as a fol
        if os.path.exists(f'./data/product_documentations/{device_name}'):
            print(f"Device {device_name} already exists")
            continue    
        zip_url = product["Compliance Document"]
        
        zip_format = zip_url.split('.')[-1]
        # Path to save the downloaded ZIP file
        zip_path = f'downloaded_zip.{zip_format}'

        # Directory to extract the ZIP file's contents
        extract_dir = './data/extracted_files'

        # Directory to store the XML files
        xml_dir = f'./data/product_documentations/{device_name}/'



        # Download the ZIP file
        print(f"Downloading {zip_url}...")
        response = requests.get(zip_url)
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        try:
            if zipfile.is_zipfile(zip_path):

                # Extract the ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif py7zr.is_7zfile(zip_path):
                with py7zr.SevenZipFile(zip_path, mode='r') as z:
                    z.extractall(path=extract_dir)
            elif rarfile.is_rarfile(zip_path):
                with rarfile.RarFile(zip_path, 'r') as z:
                    z.extractall(path=extract_dir)
            else: 
                print("The file is not a zip or 7z file")
                # Move file to a folder for manual inspection
                shutil.move(zip_path, './data/unknown_files')
                continue
        except Exception as e:
            print(e)
            # Move file to a folder for manual inspection
            if os.path.exists(f'./data/unknown_files/{device_name}.{zip_format}'):
                print(f"Device {device_name} already exists")
            shutil.move(zip_path, f'./data/unknown_files/{device_name}.{zip_format}')
            
            continue

        # Ensure xml_dir exists
        os.makedirs(xml_dir, exist_ok=True)
        # Walk through the extracted files to find XML files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.xml'):
                    # Construct full file path
                    file_path = os.path.join(root, file)
                    # Construct destination path
                    dest_path = os.path.join(xml_dir, file)
                    # Copy the XML file to the destination directory
                    shutil.copy(file_path, dest_path)

        # Clean up: remove the downloaded zip file and extracted contents
        os.remove(zip_path)
        shutil.rmtree(extract_dir)

        print("XML files have been copied to", xml_dir)
       
