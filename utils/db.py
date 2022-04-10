import pymongo
from bson.objectid import ObjectId


mongodb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")
db = mongodb['coinInfo']
coin_info_collection = db['coin_info']
coin_history_collection = db['coin_history']
alerts_collection = db['alerts']
alert_generate_collection = db['alert_generate']
coinpair_ticker_data = db['coinpair_ticker_data']

desc_sort = pymongo.DESCENDING

def clean_collection(collection_name):
    name_to_collection = {
        'coin_info':coin_info_collection,
        'coin_history':coin_history_collection,
        'alerts':alerts_collection,
        'alert_generate':alert_generate_collection,
        'coinpair_ticker_data':coinpair_ticker_data
    }
    col = name_to_collection.get(collection_name)
    if col:
        col.delete_many({})