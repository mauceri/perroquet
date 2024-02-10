import logging
import requests
import json
from datetime import datetime
from sqlite_handler import SQLiteHandler
import os



class InterrogationMixtral:
    def __init__(self,
                 db_path:str='interrogation_mixtral.sqlite',
                 profondeur_historique:int=6,
                 url:str="https://api.endpoints.anyscale.com/v1",
                 model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1",
                 instructions_initiales={"role":"system","content":"Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 500 mots, mais restent informatives."},
                 
                ):
       
        #self.load_env_variables('.localenv')
        #load_dotenv('.localenv')
        self.api_key = os.getenv('ANY_SCALE_API_KEY')
        self.db_path = db_path
        self.sqliteh = SQLiteHandler(self.db_path)
        self.profondeur_historique = profondeur_historique
        self.url = url
        self.api_key = os.getenv('ANY_SCALE_API_KEY')
        self.model_name = model_name
        self.instructions_initiales = instructions_initiales
        self.contexte = []
        #self.sqliteh.remove_all_transactions()
        #self.construction_contexte_initial()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key
        }
        

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

 
    def historique_et_question_formatés(self,utilisateur:str="kiki", salon:str="caramba"):
        contexte = [self.instructions_initiales]
        h = self.sqliteh.historique(utilisateur, salon,self.profondeur_historique)
        #print(f"Historique: {h}")
        for transaction in h:
            #print(f"transaction {transaction}")
            contexte.append({"role":"user","content":transaction['question']})
            if transaction['reponse'] != None:
                contexte.append({"role":"assistant","content":transaction['reponse']})
        print(f"Question formatée {json.dumps(contexte)}")
        #return json.dumps(contexte)
        return contexte
            

    def interroge_mixtral(self,utilisateur, salon,question):
        print(f"Interroge Mixtral {question}")
        logging.info(f"Interroge Mixtral {question}")
        qf = ""
        try:
            qf = self.historique_et_question_formatés(utilisateur, salon)
        except BaseException as e:
            print(f"Échec construction question{e}")
            logging.info(f"Échec construction question{e}")
            return None
        data = {
            "model": self.model_name,
            "messages": qf,
            "temperature": 0.7
        }
        print(f"data : {data}")
    
        try:
            reponse = requests.post(f"{self.url}/chat/completions",headers=self.headers, data=json.dumps(data))
            return reponse;
        except BaseException as e:
            print(f"Echec interrogation Mixtral {e}")
        return None

