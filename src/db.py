from pandas import DataFrame, set_option
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_database():
    client = MongoClient(os.environ['MONGO_URI'])
    return client[os.environ['DB_NAME']]

dbname = get_database()
collection_name = dbname["books"]

books = collection_name.find()
set_option('display.max_rows', None)

df = DataFrame(books)

print(df)
