from __future__ import absolute_import

import json
import os

from pymongo import MongoClient
from dotenv import load_dotenv

def connect_to_database():
    """funtion for connection to online database

    Returns:
        MongoClient: client object
    """
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    cluster_name = os.getenv('CLUSTER_NAME')
    client = MongoClient(("mongodb+srv://{0}:{1}@cluster0.9zpx1.mongodb.net/"
                          + "{2}?retryWrites=true&w=majority").format(user, password, cluster_name))
    return client
def import_json_to_db(file_name):
    """helper function to import a json file to database

    Args:
        file_name (str): name of the file

    Returns:
        dict: dictionary containing json file
    """
    client = connect_to_database()
    dictionary = None
    try:
        with open(file_name, 'r') as js_file:
            dictionary = json.load(js_file)
    except ValueError:
        print("open file failed")
        return None
    #specify database name
    data_base = client.data
    duplicate_num = 0
    sucess_num = 0
    for book in dictionary['books']:
        if data_base.books.count_documents({'_id': book['_id']}, limit=1) != 0:
            # print('duplicate book id: ' + str(book['_id']))
            duplicate_num += 1
        else:
            # result = data_base.books.insert_one(book)
            data_base.books.insert_one(book)
            # print('Created {0} book as {1}'.format(idx, result.inserted_id))
            sucess_num += 1
    print("insert {0} books into databse".format(duplicate_num + sucess_num))
    print(str(sucess_num) + " successful insertions")
    print(str(duplicate_num) + " duplicate insertions")
    duplicate_num = 0
    sucess_num = 0
    for author in dictionary['authors']:
        if data_base.authors.count_documents({'_id': author['_id']}, limit=1) != 0:
            duplicate_num += 1
        else:
            # result = data_base.authors.insert_one(author)
            data_base.authors.insert_one(author)
            # print('Created {0} author as {1}'.format(idx, result.inserted_id))
            sucess_num += 1
    print("insert {0} authors into databse".format(duplicate_num + sucess_num))
    print(str(sucess_num) + " successful insertions")
    print(str(duplicate_num) + " duplicate insertions")
    return dictionary

def export_json_from_databse(file_name):
    """helper method to export from databse to a file

    Args:
        file_name (str): output file name
    """
    client = connect_to_database()
    db = client.data
    dictionary = {}
    for collection in db.list_collection_names():
        cursor = db[collection].find({})
        dictionary[collection] = []
        document_list = dictionary[collection]
        for document in cursor:
            document_list.append(document)
    with open(file_name, 'w') as js_file:
        json.dump(dictionary, js_file)

# def insert_to_db(dictionary):
#     client = connect_to_database()
#     db = client.data

if __name__ == "__main__":
    try:
        connect_to_database()
    except:
        print("bad!")
    print("good")
