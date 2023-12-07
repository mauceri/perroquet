import unittest
from sqlite_handler import SQLiteHandler
import os
import sqlite3

class TestSQLiteHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = 'test_db.sqlite'
        cls.handler = SQLiteHandler(cls.db_path)

    def assertTableExists(self, table_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (table_name,))
            self.assertEqual(cursor.fetchone()[0], 1, f"La table {table_name} n'existe pas.")
            cursor.close()
    
    def assertTableDoesNotExist(self, table_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (table_name,))
            self.assertEqual(cursor.fetchone()[0], 0, f"La table {table_name} existe.")
            cursor.close()
    
    def test_creation_historique(self):
        #print("test_creation_historique")
        self.handler.creation_historique()
        self.assertTableExists('transactions')

    def test_suppression_historique(self):
        #print("test_suppression_historique")
        self.handler.creation_historique()  # Assurez-vous que la table existe avant de la supprimer
        self.handler.suppression_historique()
        self.assertTableExists('transactions')

    def test_creation_contexte(self):
        #print("test_creation_contexte")   
        self.handler.creation_contexte()
        self.assertTableExists('contexte')

    def test_effacement_contexte(self):
        #print("test_effacement_contexte")  
        self.handler.creation_contexte()  # Créer la table avant de la supprimer
        self.handler.effacement_contexte()
        self.assertTableDoesNotExist('contexte')

    def test_ajout_question(self):
        #print("test_creation_question") 
        self.handler.creation_historique()
        self.handler.ajout_question('123456789', 'Test question')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transactions WHERE telephone=?', ('123456789',))
            self.assertIsNotNone(cursor.fetchone(), "La question n'a pas été ajoutée.")
            cursor.close()

    # def test_modification_reponse(self):
    #     #print("test_modification_reponse") 
    #     self.handler.creation_historique()
    #     self.handler.ajout_question('123456789', 'Test question')
    #     with sqlite3.connect(self.db_path) as conn:
    #         cursor = conn.cursor()
    #         cursor.execute('SELECT transaction_id FROM transactions WHERE telephone=?', ('123456789',))
    #         transaction_id = cursor.fetchone()[0]
    #         cursor.close()
    #         cursor = conn.cursor()    
    #         self.handler.modification_reponse('123456789', transaction_id, 'Test réponse')
    #         cursor.execute('SELECT reponse FROM transactions WHERE transaction_id=?', (transaction_id,))
    #         self.assertEqual(cursor.fetchone()[0], 'Test réponse', "La réponse n'a pas été modifiée correctement.")
    #         cursor.close()

    def test_modification_reponse(self):
        #print("test_modification_reponse") 
        self.handler.creation_historique()
        transaction_id = self.handler.ajout_question('123456789', 'Test question').lastrowid
        self.handler.modification_reponse('123456789', transaction_id, 'Test réponse')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()   
            cursor.execute('SELECT reponse FROM transactions WHERE transaction_id=?', (transaction_id,))
            self.assertEqual(cursor.fetchone()[0], 'Test réponse', "La réponse n'a pas été modifiée correctement.")
            cursor.close()

    def test_modification_contexte(self):
        #print("test_modification_contexte") 
        self.handler.creation_contexte()
        self.handler.modification_contexte('123456789', {'key': 'value'})
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT contexte FROM contexte WHERE telephone=?', ('123456789',))
            contexte = cursor.fetchone()[0]
            self.assertEqual(contexte, '{"key": "value"}', "Le contexte n'a pas été modifié correctement.")
            cursor.close()

    def test_history(self):
        numero = "+33659745825"
        self.handler.ajout_question(numero, 'Qui était Henri IV de France')
        tid = self.handler.ajout_question(numero,"Qui était Henri IV de France").lastrowid
        self.handler.modification_reponse(numero, tid, "Un roi de France")
        tid = self.handler.ajout_question(numero,"Qui était Louis XIV ?").lastrowid
        self.handler.modification_reponse(numero, tid, "Le Roi Soleil")
        tid = self.handler.ajout_question(numero,"Qui était Louis XVI ?").lastrowid
        self.handler.modification_reponse(numero, tid, "Un roi de France décapité sur la place de la Révolution")
        tid = self.handler.ajout_question(numero,"Arthur Rimbaud").lastrowid
        self.handler.modification_reponse(numero, tid, "Un poète de France")
        tid = self.handler.ajout_question(numero,"Qui Paul Verlaine").lastrowid
        self.handler.modification_reponse(numero, tid, "Un autre poète de France")
        tid = self.handler.ajout_question(numero,"Qui était Jeanne d'Arc ?").lastrowid
        self.handler.modification_reponse(numero, tid, "Une jeune file qui a sauvé la France et fut brûlée vive le 30 mai 1431")
        tid = self.handler.ajout_question(numero,"Qui était Charles de Gaule").lastrowid
        self.handler.modification_reponse(numero, tid, "Un sauveur de la France")

        h = self.handler.historique(numero,4)
        self.assertEqual(len(h), 4, "Il devrait valoir 4")
        self.assertEqual(h[3]['reponse'],"Un poète de France")
        self.assertEqual(h[1]['question'],"Qui était Jeanne d'Arc ?")
        historique = []
        for transaction in h:
            historique.append({"role":"user","content":transaction['question']})
            historique.append({"role":"assistant","content":transaction['reponse']})
        print(f"Historique : {historique}")


    @classmethod
    def tearDownClass(cls):
        os.remove(cls.db_path)

if __name__ == '__main__':
    unittest.main()
