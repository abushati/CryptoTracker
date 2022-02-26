import pymongo
from bson.objectid import ObjectId


mongodb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")
db = mongodb['coinInfo']
coin_info_collection = db['coin_info']
coin_history_collection = db['coin_history']
alerts_collection = db['alerts']
alert_generate_collection = db['alert_generate']

desc_sort = pymongo.DESCENDING

def clean_collection(collection_name):
    if collection_name == 'alerts':
        col = alerts_collection
    elif collection_name == 'coin_history':
        col = coin_history_collection

    col.delete_many({})