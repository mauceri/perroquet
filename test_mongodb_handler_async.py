import unittest
import motor.motor_asyncio
import asyncio
from mongodb_handler import MongoDBHandler

class TestMongoDBHandler(unittest.TestCase):
    def setUp(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
        self.db_handler = MongoDBHandler("amigo_test", "vigogne")
        self.id = "+33659745825" 
        user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        if not user:
            doc_id = self.run_async(self.db_handler.create_user(self.id))
            print(f"Document inséré avec l'ID: {doc_id}")
        else:
            print(f"Le document {self.id} existe déjà")

    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_id(self):
        user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        if not user:
            doc_id = self.run_async(self.db_handler.create_user(self.id))
            print(f"Document inséré avec l'ID: {doc_id}")

        user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(user['_id'], self.id)
        print(user)

    def test_change_id(self):
        self.id = "+33659745826"
        user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        if not user:
            doc_id = self.run_async(self.db_handler.create_user(self.id))
            print(f"Document inséré avec l'ID: {doc_id}")

        user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(user['_id'], self.id)
        print(user)
        self.run_async(self.db_handler.delete_user(self.id))

    def test_set_profile(self):
        self.id = "+33659745825"
        self.run_async(self.db_handler.update_profile(self.id, {"prompt": "Soyez bref"}))
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(document['profile']['prompt'], "Soyez bref")
        print(document)

        self.run_async(self.db_handler.update_profile(self.id, {"prompt": "Soyez très bref"}))
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(document['profile']['prompt'], "Soyez très bref")
        print(document)

        self.run_async(self.db_handler.update_profile(self.id, {"prompt": "Soyez concis"}))
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(document['profile']['prompt'], "Soyez concis")
        print(document)
 
    def test_set_profile_field(self):
        self.id = "+33659745825"
        result = self.run_async(self.db_handler.update_profile_field(self.id, "prompt", "Soyez très bref"))
        print(f"*************************************{result}")
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(document['profile']['prompt'], "Soyez très bref")
        print(document)

        self.run_async(self.db_handler.update_profile_field(self.id, "prompt", "Soyez concis"))
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))
        self.assertEqual(document['profile']['prompt'], "Soyez concis")
        print(document)

    def test_add_transaction(self):
        self.id = "+33659745825"
        r = self.run_async(self.db_handler.add_transaction(self.id, "requête", "Qui était Henri IV de France ?"))
        print(f"********************** transaction = {r}")
        self.run_async(asyncio.sleep(1))
        document = self.run_async(self.db_handler.find_user({"_id": self.id}))

        # Pourquoi cela ne marche-t-il pas ?
        # alors que plus haut celle-ci passe 
        #user = self.run_async(self.db_handler.find_user({"_id": self.id}))
        print(f"************************{document}")

        # Supposons que vous ayez besoin de l'ID de transaction pour le test suivant
        transaction_id = document['transactions'][0]['transaction_id'] if document['transactions'] else None
        if transaction_id:
            r2 = self.run_async(self.db_handler.update_transaction_response(self.id, transaction_id, "Un roi de France"))
            print(f"Update {r2}")

    def tearDown(self):
        # Fermeture du client Motor à la fin des tests
        self.client.close()
        print("End")

if __name__ == '__main__':
    unittest.main()
