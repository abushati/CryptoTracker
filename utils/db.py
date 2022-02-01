import pymongo
from bson.objectid import ObjectId


mongodb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")
db = mongodb['coinInfo']
coin_info_collection = db['coin_info']
coin_history_collection = db['coin_history']
alerts_collection = db['alerts']

desc_sort = pymongo.DESCENDING