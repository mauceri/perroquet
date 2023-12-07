from typing import List
from collections import deque
from anyio import sleep
import requests
import sys
import json
from datetime import datetime
from interrogation_Vigogne import InterrogationVigogne
from sqlite_handler import SQLiteHandler
from transformers import AutoTokenizer



def allonzy(questions:List[str],numero:str="+33659745825"):
    iv = InterrogationVigogne(db_path='amicusdb/amicus.sqlite',)
    iv.construction_contexte_initial()
    for question in questions :
        print(f"Question du {numero}: {question}")
        transaction_id = iv.sqliteh.ajout_question(numero,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        try:
            reponse = iv.interroge_vigogne(question);
            print(f"Réponse de Vigogne \"{reponse}\"")
            r = "rien"
            r = reponse.json()["choices"][0]["text"]
            print(f"Voici la réponse: {r}")
            iv.sqliteh.modification_reponse(numero, transaction_id,r)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Vigogne {e}")
            iv.sqliteh.remove_transaction(transaction_id)
            reponse = None
            

if __name__ == "__main__":
    questions = [line.strip() for line in sys.stdin]
    allonzy(questions)
    
