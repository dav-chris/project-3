from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

#mydb = client["footballers"]
foot_db = client["footballers"]
transfers_col = foot_db["transfers"]

#print(mycol.find_one()) 

print(client.list_database_names())
print(foot_db.list_collection_names())

#client.drop_database('footballers')
#client.drop_database('footballers-transfers')
#client.drop_database('mydb')

print(transfers_col.find_one()) 