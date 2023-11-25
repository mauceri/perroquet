from pymongo import MongoClient
import unittest
from mongodb_handler import MongoDBHandler



class TestMongoDBHandler(unittest.TestCase):
        
    def setUp(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db_handler = MongoDBHandler("amigo_test", "vigogne")
        self.id = "+33659745825"
        user = self.db_handler.find_user({"_id": self.id})
        if not user:
            doc_id = self.db_handler.create_user(self.id)
            print(f"Document inséré avec l'ID: {doc_id}")
        else:
            print(f"Le document {self.id} existe déjà")

    def test_id(self):
        if not self.db_handler.find_user(self.id) :
            doc_id = self.db_handler.create_user(self.id)
            print(f"Document inséré avec l'ID: {doc_id}")

        # Trouver un document
        user = self.db_handler.find_user(self.id)
        self.assertEqual(user['_id'],self.id)
        print(user)

    def test_change_id(self):
        self.id = "+33659745826"

        if not self.db_handler.find_user(self.id) :
            doc_id = self.db_handler.create_user(self.id)
            print(f"Document inséré avec l'ID: {doc_id}")


        # Trouver un document
        user = self.db_handler.find_user(self.id)
        self.assertEqual(user['_id'],self.id)
        print(user)
        self.db_handler.delete_user(self.id)

    def test_set_profile(self):
        self.id = "+33659745825"
        self.db_handler.update_profile(self.id,{"prompt":"Soyez bref"})
        document = self.db_handler.find_user(self.id)
        self.assertEqual(document['profile']['prompt'],"Soyez bref")
        print(document)

        self.db_handler.update_profile(self.id,{"prompt":"Soyez très bref"})
        document = self.db_handler.find_user(self.id)
        self.assertEqual(document['profile']['prompt'],"Soyez très bref")
        print(document)

        self.db_handler.update_profile(self.id,{"prompt":"Soyez concis"})
        document = self.db_handler.find_user(self.id)
        self.assertEqual(document['profile']['prompt'],"Soyez concis")
        print(document)

    def test_set_profile_field(self):
        self.id = "+33659745825"
        self.db_handler.update_profile_field(self.id,"prompt","Soyez très bref")
        document = self.db_handler.find_user(self.id)
        self.assertEqual(document['profile']['prompt'],"Soyez très bref")
        print(document)

        self.db_handler.update_profile_field(self.id,"prompt","Soyez concis")
        document = self.db_handler.find_user(self.id)
        self.assertEqual(document['profile']['prompt'],"Soyez concis")
        print(document)
    
    def test_add_transaction(self):
        self.id = "+33659745825"
        r = self.db_handler.add_transaction(self.id,"requête","Qui était Henri IV de France ?")
        print(f"**************transaction = {r}")
        document = self.db_handler.find_user(self.id)
        print(f"**************{document}")

        r2 = self.db_handler.update_transaction_response(self.id, r['transaction']['transaction_id'],"Un roi de France")
        print(f"Update {r2}")

    def tearDown(self):
        #self.client.close()
        print("End")

if __name__ == '__main__':
    unittest.main()
