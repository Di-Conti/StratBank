from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv("token.env")

MDP = os.getenv('MDP')

client = MongoClient(MDP)
db = client.test

#print(client.database_names())
print(type(db))

bank = db["bank"]

#bank.insert_one(
#	{
#	"User" : "JÃ©rÃ´me Kacimi#2279",
#	"Money" : 2000,
#	"Date" : "2020-11-29",
#	}
#)

#bank.delete_many({"User" : "Sir Gouffier De Branlefort.jpeg#0625"})

compte = bank.find_one({"User": "XDDD"})
#ajout = compte["Money"] + 500
#bank.update_one({"User": "Sir Gouffier De Branlefort.jpeg#0625"}, {"$set":{"Money": ajout}})

if compte == None :
	print("oui")

cursor = bank.find()

for document in cursor :
    print('-----')
    print(document)

#print(result)


