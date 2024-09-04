import logging
import os
import time
from amicus_interfaces import IObserver, IObservable, IPlugin
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText
from amicus_bot.callbacks import Callbacks
from .sqlite_handler import SQLiteHandler
from .interrogationLocale import InterrogationLocale


sqliteh = SQLiteHandler(db_path="/data/perroquet/test_context.sqlite")
il = InterrogationLocale(sqliteh.db_path)

logger = logging.getLogger(__name__)

    
class Perroquet(IObserver):
    def __init__(self,observable:IObservable=None):
        self.__observable = observable

    def pour_llm(self,utilisateur:str,salon:str,question:str):
        print(f"Question de {utilisateur} du salon {salon}: {question}")
        transaction_id = il.sqliteh.ajout_question(utilisateur, salon,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        reponse = ""
        try:
            stime = time.time()
            reponse = il.interroge_llm(utilisateur, salon,question);
            logger.info(f"Réponse du LLM \"{reponse}\"")
            #reponse = reponse.choices[0].message.content
            reponse = reponse['choices'][0]['message']['content']
            logger.info(f"Voici la réponse: {reponse}")
            il.sqliteh.modification_reponse(utilisateur, salon, transaction_id,reponse)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation du LLM {e}")
            il.sqliteh.remove_transaction(utilisateur, salon,transaction_id)
            reponse = None
        reponset = f"{time.time()-stime} {reponse}"
        return reponset

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        logging.info(f"************ ANY_SCALE_API_KEY={os.getenv('ANY_SCALE_API_KEY')}")
        reponse = self.pour_llm(event.sender,room.display_name,msg)
        if reponse == None:
            reponse = "Une erreur s'est produite lors de l'interrogation du LLM"
        await self.__observable.notify(room, event, "Coco a dit : "+reponse, None, None)

    def prefix(self):
        return "!coco"
    
class Plugin(IPlugin):
    def __init__(self,observable:IObservable):
        self.__observable = observable
        self.perroquet = Perroquet(self.__observable)
        logger.info(f"********************** Observateur créé {self.perroquet.prefix()}")
        
    def start(self):
        logger.info(f"********************** Inscripton de {self.perroquet.prefix()}")
        self.__observable.subscribe(self.perroquet)

    async def stop(self):
        self.__observable.unsubscribe(self.perroquet)