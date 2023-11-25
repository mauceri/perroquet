from pymongo import MongoClient
import uuid
import datetime

class MongoDBHandler:
    def __init__(self, db_name, collection_name, host='localhost', port=27017):
        self.client = MongoClient(f"mongodb://{host}:{port}/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_transaction(self, telephone, type_transaction, contenu):
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "type": type_transaction,
            "contenu": contenu,
            "réponse": None,
            "timestamp_requête": datetime.datetime.now(),
            "timestamp_réponse": None
        }
        return {"res":self.collection.update_one(
                    {"_id": telephone},
                    {"$push": {"transactions": transaction}}),
                "transaction":transaction}
        
    def update_transaction_response(self, telephone, transaction_id, réponse):
        return self.collection.update_one(
            {"_id": telephone, "transactions.transaction_id": transaction_id},
            {"$set": {"transactions.$.réponse": réponse, "transactions.$.timestamp_réponse": datetime.datetime.now()}}
        )


    def get_last_transactions(self, telephone, n):
        user = self.collection.find_one({"telephone": telephone}, {"transactions": {"$slice": -n}})
        if user and "transactions" in user:
            return user["transactions"]
        return []
    
    def find_transaction_by_phone_and_timestamp(self, telephone, timestamp_requête):
        # Création de la requête
        query = {
            "_id": telephone,
            "transactions.timestamp_requête": timestamp_requête
        }

        # Projection pour filtrer uniquement la transaction correspondante
        projection = {
            "transactions.$": 1
        }

        # Exécution de la requête
        result = self.collection.find_one(query, projection)

        # Retourner la transaction si trouvée
        if result and "transactions" in result and len(result["transactions"]) > 0:
            return result["transactions"][0]  # Retourne la première transaction correspondante
        else:
            return None

    def update_profile(self, telephone, new_profile):
        print(new_profile)
        return self.collection.update_one(
            {"_id": telephone},
            {"$set": {"profile": new_profile}}
        )

    def update_profile_field(self, telephone, field, new_value):
        return self.collection.update_one(
            {"_id": telephone},
            {"$set": {f"profile.{field}": new_value}}
        )

    def create_user(self, telephone, profile={"prompt":"Soyez concis"}):
        document = {
            "_id": telephone,
            "profile": profile,
            "transactions": []
        }
        return self.collection.insert_one(document).inserted_id


    def delete_user(self, telephone):
        return self.collection.delete_one({"_id": telephone})

    def find_user(self, query):
        return self.collection.find_one(query)