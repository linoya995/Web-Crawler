import pymongo
import requests
import sys
from pymongo import MongoClient
from pathlib import *
import crawler


SUCCESS_STATUS = 200


def stored_in_database(db_name, collection_name, data_list):
    """
    Storing data in Mongo database.
    :param db_name: data base name.
    :param collection_name: collection of
    documents to be stored in database.
    :param data_list: list of dicts.
    :return: void.
    """
    # Making a Connection with MongoClient
    client = MongoClient('mongodb://localhost:27017/')

    # Getting a Database
    db = client[db_name]

    # Getting a Collection - to be stored in database
    collection = db[collection_name]

    for data in data_list:
        #Check if element with same id is already exist
        x = collection.find_one({'device_id': data.get('device_id')})
        if x is not None: collection.remove(x)

         # Inserting a Document to data base
        collection.insert_one(data).inserted_id


def download_file(file_download_link, save_folder):
    """
    Downloading files from url to a given directory.
    :param file_download_link: download link of file.
    :param save_folder: the directory where the file will saved.
    :return: void
    """

    # To get the filename, we can parse the url. fetches the last string after backslash(/).
    if file_download_link is None: return
    file_name = file_download_link.split('/')[-1]

    save_path = save_folder + str(file_name)
    try:
        req = requests.get(file_download_link)
        if req.status_code != SUCCESS_STATUS:
            print("Error: file can not be downloaded, HTTP request has been failed.")
            return

    # catch *all* exceptions
    except Exception as e:
        print("Error: file can not be downloaded %s" % str(e))
        return

    # try saving file
    try:
        with open(save_path, 'wb') as fp:
            file = req.content
            fp.write(file)
            print("file saved successfully: ", save_path)

    # catch *all* exceptions
    except Exception as e:
        print("Error: %s" % str(e))


def main(argv):
    """
       main function
    """
    if (len(argv) > 0): website_url = argv[0]   # url - to start crawling from
    else:
        print("Error: Url is missing")
        return
    download_files = True if (len(argv) > 1) and argv[1] == 'd' else False
    download_folder = argv[2] if (len(argv) > 2) else str(Path.home()) + "/Downloads/"

    # Making a Connection with MongoClient
    client = MongoClient('mongodb://localhost:27017/')

    # Getting a Database
    db = client["my_database"]

    # Getting Collections
    firmware_collection = db['firmware_collection']
    hash_collection = db['hash_collection']
    db.hash_collection.create_index([('url', pymongo.ASCENDING)], unique=True)
    db.firmware_collection.create_index([('device_id', pymongo.ASCENDING)], unique=True)

    # Start crawling
    my_crawler = crawler.Crawler()
    result = my_crawler.crawler(website_url, hash_collection)

    # Storing results in data base
    stored_in_database("my_database", 'firmware_collection', result)

    # Download files
    if download_files:
        for data in firmware_collection.find():
            download_file(data['file_download_link'], download_folder)

    # Print storing data in database
    print("Print data in firmware_collection:")
    for data in firmware_collection.find():
        print(data)


if __name__ == "__main__":
    main(sys.argv[1:])
