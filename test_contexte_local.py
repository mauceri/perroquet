import re
from typing import List
import sys
from interrogationLocale import InterrogationLocale
from sqlite_handler import SQLiteHandler
import time

sqliteh = SQLiteHandler(db_path="./perroquet_db/test_context.sqlite")
il = InterrogationLocale(db_path=sqliteh.db_path)


def pour_LLM(utilisateur:str,salon:str,question:str):
    print(f"Question de {utilisateur} du salon {salon}: {question}")
    transaction_id = il.sqliteh.ajout_question(utilisateur, salon,question).lastrowid
    print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
    try:
        reponse = il.interroge_llm(utilisateur, salon,question);
        print(f"reponse = {reponse}")
        r = reponse['choices'][0]['message']['content']
        #r = reponse.choices[0].message.content
        print(f"Voici la réponse: {r}")
    except BaseException as e:
        print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
        il.sqliteh.remove_transaction(transaction_id)
        reponse = None
 
def allonzy(lignes:List[str]):
    il.construction_contexte_initial()
    stime = time.time()
    for ligne in lignes :
        l = ligne.split(' ')
        utilisateur = ligne[0]
        salon = ligne[1]
        message = ' '.join(l[2:])
        pour_LLM(utilisateur, salon, message)
    print(f"Durée = {time.time() - stime}")

if __name__ == "__main__":
    lignes = [line.strip() for line in sys.stdin]
    allonzy(lignes)
    
