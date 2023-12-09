import logging
from typing import Dict, List, Union
from collections import deque
from anyio import sleep
import requests
import sys
import json
from datetime import datetime
from sqlite_handler import SQLiteHandler
from transformers import AutoTokenizer




class InterrogationVigogne:
    def __init__(self,
                 db_path:str='interrogation_vigogne.sqlite',
                 profondeur_historique:int=3,
                 url:str="https://mauceri--llama-cpp-python-nu-fastapi-app.modal.run",
                 instructions_initiales:Dict[str,str]={"role":"system",
                                                       "content":"Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 50 mots, mais restent informatives."},
                 tokenizer = AutoTokenizer.from_pretrained("bofenghuang/vigostral-7b-chat")                                    
                ):
        #self.numero = "+33659745825"
        self.db_path = db_path
        self.sqliteh = SQLiteHandler(self.db_path)
        self.profondeur_historique = profondeur_historique
        self.url = url
        #self.url = "https://mauceri--llama-cpp-python-nu-fastapi-app-dev.modal.run"
        self.instructions_initiales = instructions_initiales
        self.contexte = []
        self.tokenizer = tokenizer
        #self.sqliteh.remove_all_transactions()
        #self.construction_contexte_initial()
        


    def construction_contexte_initial(self,numero:str="+33659745825") :
        self.sqliteh.remove_all_transactions()
        transaction_id = self.sqliteh.ajout_question(numero,"Qui était Louis XIV de France").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Louis XIV de France est {transaction_id}")
        self.sqliteh.modification_reponse(numero, transaction_id,"Un roi de France")
        
        transaction_id = self.sqliteh.ajout_question(numero,"Qui était Charles Baudelaire").lastrowid
        #print(f"L'id de la transaction pour la question Qui était Charles Baudelaire est {transaction_id}")
        self.sqliteh.modification_reponse(numero, transaction_id,"Un poète Français")
        #for transaction in self.sqliteh.historique(numero,self.profondeur_historique):
        #    print(f"*************transaction {transaction}")

 
    def historique_et_question_formatés(self,numero:str="+33659745825"):
        contexte = [self.instructions_initiales]
        h = self.sqliteh.historique(numero,self.profondeur_historique)
        #print(f"Historique: {h}")
        for transaction in h:
            #print(f"transaction {transaction}")
            contexte.append({"role":"user","content":transaction['question']})
            if transaction['reponse'] != None:
                contexte.append({"role":"assistant","content":transaction['reponse']})
        #contexte.append({"role":"user","content":question})
        print(f"Question avant formatage {contexte}")
        logging.info(f"Question avant formatage {contexte}")
        try:
            question_formatée = self.tokenizer.apply_chat_template(contexte, tokenize=False, add_generation_prompt=True,use_fast=False)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau du tokenizer{e}")
            logging.info(f"Quelque chose n'a pas fonctionné au niveau du tokenizer{e}")
            return f"Quelque chose n'a pas fonctionné {e}"
        #print(f"Question formatée {question_formatée}")
        return question_formatée

    def interroge_vigogne(self,numero,question):
        print(f"Interroge Vigogne {question}")
        logging.info(f"Interroge Vigogne {question}")
        qf = ""
        try:
            qf = self.historique_et_question_formatés(numero)
        except BaseException as e:
            print(f"Échec construction question{e}")
            logging.info(f"Échec construction question{e}")
            return None
        item = {"question":qf}
        print(f"Interrogation de Vigogne |{item}|")
        logging.info(f"Interrogation de Vigogne |{item}|")
        try:
            reponse = "rien"
            reponse = requests.post(f"{self.url}/question", json=item)
            return reponse;
        except BaseException as e:
            print(f"Echec interrogation Vigogne {e}")
        return None

