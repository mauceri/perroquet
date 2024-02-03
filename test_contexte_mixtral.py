import re
from typing import List
from collections import deque
from anyio import sleep
import requests
import sys
import json
from datetime import datetime
from interrogation_Mixtral import InterrogationMixtral
from sqlite_handler import SQLiteHandler
from transformers import AutoTokenizer


class InterpreteurDeMessage:
    def __init__(self,db_path:str='test_contexte.sqlite'):
        self.commandes = ["--aide:","--profil:","--maj_profil:"]
        self.sqliteh = SQLiteHandler(db_path=db_path)
        self.iv = InterrogationMixtral(db_path=db_path)

    def commande(self,commande,arguments):
        onsexcuze = f'''La commande {commande} {arguments} devrait êre disponible incessament sous peu et peut-être même avant'''
        aide = '''La maison est fière de vous annoncer qu'amicus vous proposera bientôt :
        --profil: une commande qui affichera votre profil
        --maj_profil: une commande vous permettant de mettre votre profil à jour
        --aide: cette même commande qui sera améliorée de façon à ce que même vous puissiez comprendre'''
        if commande == "--aide" :
            print(aide)
            return aide;
        else:
            print(onsexcuze)
            return onsexcuze

    def quoi(self,message:str)->str:
        # Divise la chaîne en deux parties : 'quoi' et 'reste'
        quoi, *reste = message.split(maxsplit=1)
        # Convertit 'reste' en une seule chaîne si nécessaire
        reste = ' '.join(reste)
        return quoi, reste

    def est_ce_une_commandeq(self,quoi:str) -> bool:
        return quoi in self.commandes

    def est_ce_un_numeroq(self,quoi:str)->bool:
        # Expression régulière pour un numéro de téléphone international
        motif = r"\+[0-9]+"
        # Vérifie si la chaîne correspond au motif
        return re.match(motif, quoi) is not None

    def distribution(self,message:str,premier:bool=True,numero:str=""):
        quoi, reste = self.quoi(message) 
        
        if self.est_ce_un_numeroq(quoi) and premier:
            self.distribution(reste,False,quoi)
        elif self.est_ce_une_commandeq(quoi) and not premier: 
            self.commande(quoi, reste)
        elif not premier and not numero == "":
            self.pour_Mixtral(numero,quoi+" "+reste)           
        else:
            print(f"Erreur js ne sais pas quoi faire de {message} et {numero}")

    def pour_Mixtral(self,numero:str,question:str):
        print(f"Question du {numero}: {question}")
        transaction_id = self.iv.sqliteh.ajout_question(numero,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        try:
            reponse = self.iv.interroge_mixtral(numero,question);
            print(f"Réponse de Mixtral \"{reponse}\"")
            r = "rien"
            r = reponse.json()["choices"][0]["message"]["content"]
            print(f"Voici la réponse: {r}")
            self.iv.sqliteh.modification_reponse(numero, transaction_id,r)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
            self.iv.sqliteh.remove_transaction(transaction_id)
            reponse = None

    def allonzy(self,lignes:List[str]):
        self.iv.construction_contexte_initial()
        for ligne in lignes :
            self.distribution(ligne)
            

if __name__ == "__main__":
    lignes = [line.strip() for line in sys.stdin]
    idm = InterpreteurDeMessage()
    idm.allonzy(lignes)
    
