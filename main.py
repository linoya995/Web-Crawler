import pymongoimport requestsimport sysfrom pymongo import MongoClientfrom pathlib import *import crawlerERROR_STATUS = 404SUCCESS_STATUS = 200def stored_in_database(db_name, collection_name, result):    """    store data in Mongo database.    Parameters:    db - data base object.    data - the data to be inserted, for example: a dict.    collection - is a group of documents stored in MongoDB, and    can be thought of as roughly the equivalent of a table in a    relational database.    """    # Making a Connection with MongoClient    client = MongoClient('mongodb://localhost:27017/')    # Getting a Database    db = client[db_name]    # Getting a Collection - is a group of documents stored in MongoDB    # equivalent of a table in a relational database    collection = db[collection_name]    for data_dict in result:        print(data_dict)        # Inserting a Document to data base        post_id = collection.insert_one(data_dict).inserted_iddef download_file(file_download_link, save_folder, file_name=''):    """    Download files from url to a given directory.    Parameters:    file_download_link - url link for downloading file.    file_name - name of the file that will be downloaded.    save_folder - the directory where the file will saved.    """    # To get the filename, we can parse the url. fetches the last string after backslash(/).    if file_name == '': name = file_download_link.split('/')[-1]    save_path = save_folder + file_name    try:        req = requests.get(file_download_link)        if req.status_code != SUCCESS_STATUS:            print("Error: file can not be downloaded, HTTP request has been failed.")    # catch *all* exceptions    except Exception as e:        print("Error: %s" % str(e))    # try saving file    try:        with open(save_path, 'wb') as fp:            file = req.content            fp.write(file)            print("file saved successfully: ", save_path)    # catch *all* exceptions    except Exception as e:        print("Error: %s" % str(e))def main(argv):    """       main function.    """    website_url = argv[0]  # url - to start crawling from    download_files = True if (len(argv) > 2) and argv[1] == 'd' else False    download_folder = argv[2] if (len(argv) > 3) else str(Path.home()) + "/Downloads/"    # Making a Connection with MongoClient    client = MongoClient('mongodb://localhost:27017/')    # Getting a Database    db = client["my_database"]    # Getting Collections    #db.drop_collection('hash_collection')    firmware_collection = db['firmware_collection']    hash_collection = db['hash_collection']    db.hash_collection.create_index([('url', pymongo.ASCENDING)], unique=True)    db.firmware_collection.create_index([('device_id', pymongo.ASCENDING)], unique=True)    # Print    print(db.list_collection_names())    for data in hash_collection.find():        print(data)    # Start crawling    my_crawler = crawler.Crawler()    result = my_crawler.crawler(website_url, hash_collection)    # Storing results in data base    stored_in_database("my_database", 'firmware_metadata', result)    # Print    print(db.list_collection_names())    for data in firmware_collection.find():        print(data)    # Download files    if download_files:        for data in firmware_collection.find():            download_file(data['file_download_link'],download_folder,data['file_name'])if __name__ == "__main__":    main(sys.argv[1:])