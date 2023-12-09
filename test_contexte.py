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

def extraire_numero_questions(chaine):
    # Divise la chaîne en deux parties : 'numero' et 'questions'
    numero, *question = chaine.split(maxsplit=1)
    
    # Convertit 'arguments' en une seule chaîne si nécessaire
    question = ' '.join(question)
    
    return numero, question

def allonzy(lignes:List[str]):
    iv = InterrogationVigogne(db_path='test_contexte.sqlite',)
    iv.construction_contexte_initial()
    for ligne in lignes :
        numero, question = extraire_numero_questions(ligne)
        print(f"Question du {numero}: {question}")
        transaction_id = iv.sqliteh.ajout_question(numero,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        try:
            reponse = iv.interroge_vigogne(numero,question);
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
    lignes = [line.strip() for line in sys.stdin]
    allonzy(lignes)
    
