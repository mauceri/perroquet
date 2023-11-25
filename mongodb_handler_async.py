import motor.motor_asyncio
import uuid
import datetime

class MongoDBHandler:
    def __init__(self, db_name, collection_name, host='localhost', port=27017):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{host}:{port}/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def add_transaction(self, telephone, type_transaction, contenu):
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "type": type_transaction,
            "contenu": contenu,
            "réponse": None,
            "timestamp_requête": datetime.datetime.now(),
            "timestamp_réponse": None
        }
        result = await self.collection.update_one(
                    {"_id": telephone},
                    {"$push": {"transactions": transaction}})
        return result

    async def update_transaction_response(self, telephone, transaction_id, réponse):
        return await self.collection.update_one(
            {"_id": telephone, "transactions.transaction_id": transaction_id},
            {"$set": {"transactions.$.réponse": réponse, "transactions.$.timestamp_réponse": datetime.datetime.now()}}
        )

    async def get_last_transactions(self, telephone, n):
        user = await self.collection.find_one({"_id": telephone}, {"transactions": {"$slice": -n}})
        if user and "transactions" in user:
            return user["transactions"]
        return []

    async def find_transaction_by_phone_and_timestamp(self, telephone, timestamp_requête):
        query = {
            "_id": telephone,
            "transactions.timestamp_requête": timestamp_requête
        }
        projection = {
            "transactions.$": 1
        }
        result = await self.collection.find_one(query, projection)
        if result and "transactions" in result and len(result["transactions"]) > 0:
            return result["transactions"][0]
        else:
            return None

    async def update_profile(self, telephone, new_profile):
        return await self.collection.update_one(
            {"_id": telephone},
            {"$set": {"profile": new_profile}}
        )

    async def update_profile_field(self, telephone, field, new_value):
        return await self.collection.update_one(
            {"_id": telephone},
            {"$set": {f"profile.{field}": new_value}}
        )

    async def create_user(self, telephone, profile={"prompt": "Soyez concis"}):
        document = {
            "_id": telephone,
            "profile": profile,
            "transactions": []
        }
        result = await self.collection.insert_one(document)
        return result.inserted_id
    
    async def delete_user(self, telephone):
        return await self.collection.delete_one({"_id": telephone})

    async def find_user(self, query):
        return await self.collection.find_one(query)
