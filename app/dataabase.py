from motor.motor_asyncio import AsyncIOMotorClient


MONGO_DETAILS = "mongodb://localhost:27017"  


client = AsyncIOMotorClient(MONGO_DETAILS)

database = client.real_estate_db  

property_collection = database.get_collection("properties")   

user_collection = database.get_collection("users")

property_collection = database.get_collection("properties")
user_collection = database.get_collection("users")


saved_search_collection = database.get_collection("saved_searches")
