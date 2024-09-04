import logging
import requests
import json
from datetime import datetime
from .sqlite_handler import SQLiteHandler
import os

class InterrogationLocale:
    def __init__(self,
                 db_path: str = 'interrogation_mixtral.sqlite',
                 profondeur_historique: int = 6,
                 url: str = "http://100.90.227.83:8000/v1",  # Nouvelle URL
                 model_name="Phi-3.5-mini-instruct-Q6_K.gguf",
                 instructions_initiales={"role": "system", "content": "Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 500 mots, mais restent informatives."},
                 ):
        
        self.db_path = db_path
        self.sqliteh = SQLiteHandler(self.db_path)
        self.profondeur_historique = profondeur_historique
        self.url = url
        self.model_name = model_name
        self.instructions_initiales = instructions_initiales
        self.contexte = []

    def load_env_variables(self,file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    def construction_contexte_initial(self,utilisateur:str="kiki", salon:str="caramba") :
        self.sqliteh.remove_all_transactions()
        transaction_id = self.sqliteh.ajout_question(utilisateur, salon,"Qui était Louis XIV de France").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Louis XIV de France est {transaction_id}")
        self.sqliteh.modification_reponse(utilisateur, salon, transaction_id,"Un roi de France")
        
        transaction_id = self.sqliteh.ajout_question(utilisateur, salon,"Qui était Charles Baudelaire").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Charles Baudelaire est {transaction_id}")
        self.sqliteh.modification_reponse(utilisateur, salon, transaction_id,"Un poète Français")
        #for transaction in self.sqliteh.historique(utilisateur, salon,self.profondeur_historique):
        #    print(f"*************transaction {transaction}")

    def historique_et_question_formatés(self, utilisateur: str = "kiki", salon: str = "caramba"):
        contexte = [self.instructions_initiales]
        h = self.sqliteh.historique(utilisateur, salon, self.profondeur_historique)
        for transaction in h:
            contexte.append({"role": "user", "content": transaction['question']})
            if transaction['reponse'] is not None:
                contexte.append({"role": "assistant", "content": transaction['reponse']})
        return contexte

    def interroge_llm(self, utilisateur, salon, question):
        print(f"Interroge {self.model_name} {question}")
        logging.info(f"Interroge {self.model_name} {question}")
        try:
            qf = self.historique_et_question_formatés(utilisateur, salon)
        except BaseException as e:
            print(f"Échec construction question {e}")
            logging.info(f"Échec construction question {e}")
            return None
        
        # Préparation des headers pour la requête POST
        headers = {
            "Content-Type": "application/json",
#            "Authorization": f"Bearer {self.api_key}"  # Utilisation de la clé API si nécessaire
        }
        
        print(f"°°°°°°°°°°°°°°°°°°°°°°°°°°°°°° qf = {qf}")

        # Préparation des données pour l'appel à la nouvelle API
        data = {
            "model": self.model_name,
            "messages": qf,
            "temperature": 0.7
        }

        try:
            # Appel à la nouvelle URL avec requests.post
            response = requests.post(f"{self.url}/chat/completions", headers=headers, data=json.dumps(data))

            # Vérification de la réponse
            if response.status_code == 200:
                return response.json()  # Retourne la réponse formatée JSON
            else:
                print(f"Échec interrogation locale : {response.status_code}, {response.text}")
                logging.info(f"Échec interrogation locale : {response.status_code}, {response.text}")
                return None
        except BaseException as e:
            print(f"Échec interrogation Mixtral {e}")
            logging.info(f"Échec interrogation Mixtral {e}")
            return None

