import os
import re
import json
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


import threading
from threading import Thread

function_lock = threading.Lock()

# ------- GCloud Storage Configuration ----------

# import packages
import os
from os import listdir
from os.path import isfile, join
from dotenv import load_dotenv
from google.cloud import storage

# key credentials file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "env/ai-chatbot-412021-e1606cdc6784.json"

bucketName = "tas-website-data"

# -------------------------------------------

# ------------ GCloud Files Access / Modify Functions ----------------

def delete_merged_vector(bucket_name = bucketName):

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

def upload_merged_vector(bucket_name = bucketName):

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

def del_n_upload_csv_database(bucket_name = bucketName):

    local_file_path = "database.csv"
    gcs_file_name = "database.csv"

    # Initialize a Google Cloud Storage client
    client = storage.Client()

    # Get the bucket object
    bucket = client.get_bucket(bucket_name)

    # Delete the existing file from GCS if it exists
    blob = bucket.get_blob(gcs_file_name)
    if blob:
        blob.delete()
        print(f"Deleted '{gcs_file_name}' from GCS.")

    # Upload the new file from the local path to GCS
    new_blob = bucket.blob(gcs_file_name)
    new_blob.upload_from_filename(local_file_path)
    print(f"Uploaded '{local_file_path}' to '{gcs_file_name}' in GCS.")

    # Return True to indicate success
    return "Successfull !!!"

# -------------------------------------------------



# -------------------- Dependencies for the Main Function ----------------

def download_xml_by_id(xml_id, type, callback):
    xml_url = f"https://www.theartstory.org/data/content/{type}/{xml_id}.xml"
    output_folder = f"data/raw_xmls/{type}s"
    output_file = f"data/raw_xmls/{type}s/{xml_id}.xml"
    try:
        # Make a GET request to the XML URL
        try:
            response = requests.get(xml_url, timeout=5)
        except Exception as e:
            print(f"Download Function Error - Python Requests Library Error : {e}")
            output = f"Download Function Error - Python Requests Library Error : {e}"
            callback(output)
            return False

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the output file in binary write mode and write the XML content
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            if os.path.exists(output_file):
                os.remove(output_file)
            
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

def convert_to_underscore(input_string):
    # Using regex to replace hyphens with underscores
    result_string = re.sub(r'[-]', '_', input_string)
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
        print(f"{xml_id} - No Changes Found")
    else:
        print(f"{xml_id} - Changes are Found")

    # Compare the XML structures
    return similarity_response

# ---------------------------------------------------------------



# -----------------  MAIN DRIVER FUNCTION -----------------------

def filter_and_store_paths(callback):

    output = ""      # Sends to WebSocket

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

    if not os.path.exists("data/faq"):
        os.makedirs("data/faq")
    if not os.path.exists("data/faq/faq.txt"):
        with open("data/faq/faq.txt", "w") as faq_file:
            faq_file.write("Sample FAQ File")
            output = f"Built Sample FAQ File"
            callback(output)
    else:
        output = f"Found FAQ File"
        callback(output)
    
    if not os.path.exists("data/merged_vector/index.faiss"):
        first_vectorise()
        print(f"FAQ File Vectorised")
        output = f"FAQ File Vectorised"
        callback(output)
    else:
        refresh_faq_vector()
        print(f"FAQ File Updated and Vectorised")
        output = f"FAQ File Updated and Vectorised"
        callback(output)
    

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
        print(f"Part - 1 : Error in Sitemap Scrapping : {e}")
        output = f"Part - 1 : Error in Sitemap Scrapping : {e}"
        callback(output)
    
    print(f"Successfully Scraped Sitemap... Extracting Data...")
    output = f"Successfully Scraped Sitemap... Extracting Data..."
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

            # ================  CONDITION IS HERE ======================
            #===========================================================
            # Modify this condition to filter the required type / id
            if extracted_type!="add condition here":
            # if extracted_type=="critic":

                output = f"\n\n==> Checking File {count} out of {total_paths} : {extracted_type} - {extracted_xml_id}"
                callback(output)
                

                #-----------------  NEW FILES  -------------------

                # For New Files, Check ID in DB; if Not exist; then Download and Add to DB

                if (is_value_in_csv(extracted_xml_id) == False):

                    print(f"New Value : {extracted_type} - {extracted_xml_id}. NOT Found in DB")
                    output = f"New File Detected : {extracted_type} - {extracted_xml_id}"
                    callback(output)

                    # Downloading Files
                    downloaded = download_xml_by_id(extracted_xml_id, extracted_type, callback)
                    if (downloaded == False):
                        print("\nDownload Failed, Going to the Next One...")
                        continue
                    output = "Successfully Downloaded."
                    callback(output)

                    record_to_add = [extracted_type, extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), " - ", " - ", "here_should_be_the_name"]
                    add_record(record_to_add)

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
                    output = "Successsfully Filtered."
                    callback(output)

                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 3)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 4)
                    update_record(extracted_xml_id, extracted_name, 5)

                    add_to_vector(extracted_xml_id, extracted_type)
                    output = "Successsfully Vectorised."
                    callback(output)

                if (are_xml_files_equal(extracted_xml_id, extracted_type) ==  False):
                    output = f"Change Detected : {extracted_type} - {extracted_xml_id}"
                    callback(output)

                    download_xml_by_id(extracted_xml_id, extracted_type, callback)
                    output = "Successfully Downloaded."
                    callback(output)

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
                    output = "Successsfully Filtered."
                    callback(output)

                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 3)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 2)
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 4)
                    update_record(extracted_xml_id, extracted_name, 5)

                    refresh_vector(extracted_xml_id, extracted_type)
                    output = "Successfully Vectorised."
                    callback(output)

                else:
                    update_record(extracted_xml_id, str(datetime.now().strftime("%d %B %Y %H:%M")), 2)
                    output = f"NO Change Detected : {extracted_type} - {extracted_xml_id} - Skipping"
                    callback(output)
    
    output = f"\n\nDeleting Existing VectorDatabase From Cloud  --> {delete_merged_vector()}"
    callback(output)
    output = f"\n\nUploading Updated VectorDatabase To Cloud --> {upload_merged_vector()}"
    callback(output)
    output = f"\n\nUploading modified database.csv To Cloud --> {del_n_upload_csv_database()}"
    callback(output)

    output = f"\n\n--------------------\n\nCompleted !!!\n\n-------------------------"
    callback(output)

    print(f"Filtered paths extracted and stored in database.csv and Required Folder")
    return "Success"


def start_my_function(callback):
    if function_lock.locked():
        return False

    with function_lock:
        thread = threading.Thread(target=filter_and_store_paths, args=(callback,))
        thread.start()

    return True