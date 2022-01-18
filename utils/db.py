import pymongo
mongodb = pymongo.MongoClient("mongodb+srv://tracker:admin@cluster0.szrgk.mongodb.net/test")
db = mongodb['coinInfo']
desc_sort  = pymongo.DESCENDING