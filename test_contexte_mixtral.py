import re
from typing import List
import sys
from interrogationMixtralAnyscale import InterrogationMixtral
from sqlite_handler import SQLiteHandler

sqliteh = SQLiteHandler(db_path="./test_context.sqlite")
im = InterrogationMixtral(db_path=sqliteh.db_path)


def pour_Mixtral(utilisateur:str,salon:str,question:str):
    print(f"Question de {utilisateur} du salon {salon}: {question}")
    transaction_id = im.sqliteh.ajout_question(utilisateur, salon,question).lastrowid
    print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
    try:
        reponse = im.interroge_mixtral(utilisateur, salon,question);
        print(f"Réponse de Mixtral \"{reponse}\"")
        r = reponse.json()["choices"][0]["message"]["content"]
        print(f"Voici la réponse: {r}")
        #self.iv.sqliteh.modification_reponse(numero, transaction_id,r)
    except BaseException as e:
        print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
        im.sqliteh.remove_transaction(transaction_id)
        reponse = None
 
def allonzy(lignes:List[str]):
    im.construction_contexte_initial()
    for ligne in lignes :
        l = ligne.split(' ')
        utilisateur = ligne[0]
        salon = ligne[1]
        message = ' '.join(l[2:])
        pour_Mixtral(utilisateur, salon, message)

            

if __name__ == "__main__":
    lignes = [line.strip() for line in sys.stdin]
    allonzy(lignes)
    
