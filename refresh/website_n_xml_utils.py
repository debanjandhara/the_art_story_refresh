import os
import requests
import time
from datetime import datetime

from .models.models import *
from .vectorisation.vector_create_n_query import *
from .xml_filtration.format_artist_xml import *
from .xml_filtration.format_critic_xml import *
from .xml_filtration.format_definition_xml import *
from .xml_filtration.format_influencer_xml import *
from .xml_filtration.format_movement_xml import *
from .test import *

import time
from threading import Thread

# -------------------------------------------

# import packages
from google.cloud import storage
import os
from os import listdir
from os.path import isfile, join
from dotenv import load_dotenv

# set key credentials file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "env/ai-chatbot-412021-e1606cdc6784.json"

bucketName = "tas-website-data"

# -------------------------------------------

def download_xml_by_id(xml_id, type, callback):
    xml_url = f"https://www.theartstory.org/data/content/{type}/{xml_id}.xml"
    output_folder = f"data/raw_xmls/{type}s"
    output_file = f"data/raw_xmls/{type}s/{xml_id}.xml"
    try:
        # Make a GET request to the XML URL
        try:
            response = requests.get(xml_url, timeout=5)
        except Exception as e:
            print(f"Download Function Error : {e}")
            output = f"Download Function Error : {e}"
            callback(output)
            return False

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the output file in binary write mode and write the XML content
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            if os.path.exists(output_file):
                # If it exists, delete the file
                os.remove(output_file)
                print(f"Deleted existing file: {output_file}")
            else:
                print("File Doesn't Exists")
            
            with open(output_file, 'wb') as file:
                file.write(response.content)
            
            print(f"XML downloaded successfully and saved at {output_file}")
            return True
        else:
            print(f"Error: Unable to download XML. Status Code: {response.status_code}")
            output = f"Error: Unable to download XML. Status Code: {response.status_code}"
            callback(output)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False



import re
import json

import re
import json

def convert_to_underscore(input_string):
    # Using regex to replace hyphens with underscores
    result_string = re.sub(r'[-]', '_', input_string)
    print(result_string.encode('utf-8'))
    return result_string


def are_xml_files_equal(xml_id, type):

    import xml.etree.ElementTree as ET

    online_url = f"https://www.theartstory.org/data/content/{type}/{xml_id}.xml"
    local_path = f"data/raw_xmls/{type}s/{xml_id}.xml"
    
    # Fetch online XML
    online_response = requests.get(online_url)
    online_tree = ET.ElementTree(ET.fromstring(online_response.content))

    # Read locally stored XML
    with open(local_path, 'rb') as local_file:
        local_tree = ET.ElementTree(ET.fromstring(local_file.read()))
    
    similarity_response = ET.tostring(online_tree.getroot()) == ET.tostring(local_tree.getroot())
    
    if similarity_response == True:
        print(f"{xml_id} --> Files are Same")
    else:
        print(f"{xml_id} --> Files are Different")

    # Compare the XML structures
    return similarity_response

def delete_folder(bucket_name = bucketName):

    import os
    from google.cloud import storage

    folder_name = "data/merged_vector/"
    # Instantiates a client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # List all blobs in the folder
    blobs = bucket.list_blobs(prefix=folder_name)

    # Delete each blob in the folder
    for blob in blobs:
        blob.delete()

    print(f"Folder '{folder_name}' deleted successfully.")
    return "Successfull !!!"

def upload_files(bucket_name = bucketName):

    import os
    from google.cloud import storage

    local_folder_path = "data/merged_vector"
    cloud_folder_path = "data/merged_vector"

    # Instantiates a client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Creating a Folder in Bucket
    blob = bucket.blob(f"{cloud_folder_path}/")

    # List all files in the local folder
    local_files = os.listdir(local_folder_path)

    # Upload each file to the cloud folder
    for local_file in local_files:
        local_file_path = os.path.join(local_folder_path, local_file)
        cloud_file_path = os.path.join(cloud_folder_path, local_file)

        cloud_file_path = cloud_file_path.replace("\\", "/")

        blob = bucket.blob(cloud_file_path)
        blob.upload_from_filename(local_file_path)

        print(f"File '{local_file}' uploaded to '{cloud_file_path}'.")
    
    return "Successfull !!!"

def filter_and_store_paths(callback):

    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse, urljoin

    # Creating my data folders if they don't exist 

    if not os.path.exists("data/"):
        os.makedirs("data/")
    if not os.path.exists("data/filtered_txts"):
        os.makedirs("data/filtered_txts")
    if not os.path.exists("data/filtered_txts/artists"):
        os.makedirs("data/filtered_txts/artists")
    if not os.path.exists("data/filtered_txts/critics"):
        os.makedirs("data/filtered_txts/critics")
    if not os.path.exists("data/filtered_txts/definitions"):
        os.makedirs("data/filtered_txts/definitions")
    if not os.path.exists("data/filtered_txts/influencers"):
        os.makedirs("data/filtered_txts/influencers")
    if not os.path.exists("data/filtered_txts/movements"):
        os.makedirs("data/filtered_txts/movements")
    if not os.path.exists("data/raw_xmls"):
        os.makedirs("data/raw_xmls")
    if not os.path.exists("data/raw_xmls/artists"):
        os.makedirs("data/raw_xmls/artists")
    if not os.path.exists("data/raw_xmls/critics"):
        os.makedirs("data/raw_xmls/critics")
    if not os.path.exists("data/raw_xmls/definitions"):
        os.makedirs("data/raw_xmls/definitions")
    if not os.path.exists("data/raw_xmls/influencers"):
        os.makedirs("data/raw_xmls/influencers")
    if not os.path.exists("data/raw_xmls/movements"):
        os.makedirs("data/raw_xmls/movements")

    # Define the URL to scrape
    url = "https://www.theartstory.org/sitemap.htm"

    # Inintializing the count for the files
    count = 0

    try:
        # Fetch the HTML content of the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Define paths to filter
        filter_paths = ["/artist/", "/critic/", "/definition/", "/influencer/", "/movement/"]

        # Extract and filter paths from the links
        paths = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            path = urlparse(full_url).path
            if any(filter_path in path for filter_path in filter_paths):
                paths.add(path)
        total_paths = len(paths)
    except Exception as e:
        print(f"Part - 1 : Unexpected error: {e}")
        output = f"Part - 1 : Unexpected error: {e}"
        callback(output)

    for path in paths:
        output = ""
        count += 1
        if (count < 10000): # Limit the File Count and Check for the First 10 Files

            # Splitting the string using "/" as the delimiter
            segments = path.split("/")

            # Extracting the first and second portions
            extracted_type = segments[1]
            extracted_id = segments[2]
            extracted_xml_id = convert_to_underscore(extracted_id)

            # Modify this condition to filter the required type / id
            if extracted_type!="add condition here":
            # if extracted_type=="critic":

                output = f"=== Checking File {count} out of {total_paths} : {extracted_type} - {extracted_xml_id}"
                callback(output)

                #-----------------  NEW FILES  -------------------

                # For New Files, Check ID in DB; if Not exist; then Download and Add to DB

                if (is_value_in_csv(extracted_xml_id) == False):

                    print(f"\nIts a New Value. Value : \"{extracted_xml_id}\" not Found in DB")

                    # Downloading Files
                    downloaded = download_xml_by_id(extracted_xml_id, extracted_type, callback)
                    if (downloaded == False):
                        print("\nDownload Failed, Going to the Next One...")
                        continue

                    record_to_add = [extracted_type, extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), " - ", " - ", "here_should_be_the_name"]
                    add_record(record_to_add)
                    print(f"\nAdded New Record for {extracted_xml_id}")

                    try:
                        # Filter and Store XML
                        if extracted_type == "artist":
                            extracted_name = artist_xml(extracted_xml_id)
                        if extracted_type == "critic":
                            extracted_name = critic_xml(extracted_xml_id)
                        if extracted_type == "definition":
                            extracted_name = definition_xml(extracted_xml_id)
                        if extracted_type == "movement":
                            extracted_name = movement_xml(extracted_xml_id)
                        if extracted_type == "influencer":
                            extracted_name = influencer_xml(extracted_xml_id)
                    except Exception as e:
                        print(f"Filtration Problem - XML Tags Different : Unexpected error: {e}")
                        output = f"Filtration Problem - XML Tags Different : Unexpected error: {e}"
                        callback(output)

                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 3)
                    print(f"\nUpdated Exisitng Record for {extracted_xml_id}")
                    # vectorise(extracted_xml_id, extracted_type)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 4)
                    print(extracted_xml_id)
                    update_record(extracted_xml_id, extracted_name, 5)

                    output = "-- New File Detected ..."
                    callback(output)
                    output = "-- Downloaded --"
                    callback(output)
                    output = "-- Filtered --"
                    callback(output)
                    output = "-- Vectorised --"
                    callback(output)

                if (are_xml_files_equal(extracted_xml_id, extracted_type) ==  False):
                    output = "-- Files are Different --"
                    callback(output)
                    output = "-- Downloaded --"
                    callback(output)
                    output = "-- Filtered --"
                    callback(output)
                    output = "-- Vectorised --"
                    callback(output)
                    download_xml_by_id(extracted_xml_id, extracted_type, callback)
                    if extracted_type == "artist":
                        extracted_name = artist_xml(extracted_xml_id)
                    if extracted_type == "critic":
                        extracted_name = critic_xml(extracted_xml_id)
                    if extracted_type == "definition":
                        extracted_name = definition_xml(extracted_xml_id)
                    if extracted_type == "movement":
                        extracted_name = movement_xml(extracted_xml_id)
                    if extracted_type == "influencer":
                        extracted_name = influencer_xml(extracted_xml_id)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 3)
                    try:
                        update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 2)
                    except Exception as e:
                        print(f"Part - 2.2 : Unexpected error: {e}")
                        output = f"Part - 2.2 : Unexpected error: {e}"
                        callback(output)
                    # vectorise(extracted_xml_id, extracted_type)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 4)
                    update_record(extracted_xml_id, extracted_name, 5)
                else:
                    output = "-- Files are Same -- Skipping..."
                    callback(output)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 2)
    output = f"\n\nMerged --> {merge_db(callback)}"
    callback(output)
    output = f"Completed !!!"
    callback(output)
    # # output = f"\n\nDeleted Existing  --> {delete_folder()}"
    # # callback(output)
    # # output = f"\n\nUpdated VectorDB --> {upload_files()}"
    # # callback(output)
                    
# ----------------------------------------------------------------------------------------------------------------------------


    print(f"Filtered paths extracted and stored in database.csv and Required Folder")
    return "Success"

def start_my_function(callback):
    # thread = Thread(target=my_function, args=(callback,))
    thread = Thread(target=filter_and_store_paths, args=(callback,))
    thread.start()

# filter_and_store_paths()