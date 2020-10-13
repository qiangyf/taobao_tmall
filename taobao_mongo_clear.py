import pymongo


def clear_mongo_data():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["taobao"]
    mycol = mydb["t2"]
    mycol2 = mydb['t_clear']
    good_ids = []

    for x in mycol.find():
        good_id = x['good_id']
        if good_id not in good_ids:
            good_ids.append(good_id)
            mycol2.insert_one(x)
        else:
            pass

clear_mongo_data()