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
        # Inserting a Document to data base
        collection.insert_one(data).inserted_id


def download_file(file_download_link, save_folder, file_name=''):
    """
    Downloading files from url to a given directory.
    :param file_download_link: download link of file.
    :param save_folder: the directory where the file will saved.
    :param file_name: the name of the file. if it is not set,
    get file name by parsing url..
    :return: void
    """

    # To get the filename, we can parse the url. fetches the last string after backslash(/).
    if file_name == '': name = file_download_link.split('/')[-1]

    save_path = save_folder + file_name
    try:
        req = requests.get(file_download_link)
        if req.status_code != SUCCESS_STATUS:
            print("Error: file can not be downloaded, HTTP request has been failed.")

    # catch *all* exceptions
    except Exception as e:
        print("Error: %s" % str(e))

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
       main function.
    """
    website_url = argv[0]  # url - to start crawling from
    download_files = True if (len(argv) > 2) and argv[1] == 'd' else False
    download_folder = argv[2] if (len(argv) > 3) else str(Path.home()) + "/Downloads/"

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
            download_file(data['file_download_link'], download_folder, data['file_name'])

    # Print storing data in database
    print("Print data in firmware_collection:")
    for data in firmware_collection.find():
        print(data)


if __name__ == "__main__":
    main(sys.argv[1:])
