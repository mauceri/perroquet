import logging
from amicus_interfaces import IObserver, IObservable, IPlugin
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText
from amicus_bot.callbacks import Callbacks
from .sqlite_handler import SQLiteHandler
from .interrogationMixtralAnyscale import InterrogationMixtral


sqliteh = SQLiteHandler(db_path="/data/perroquet/test_context.sqlite")
im = InterrogationMixtral(sqliteh.db_path)

logger = logging.getLogger(__name__)

    
class Perroquet(IObserver):
    def __init__(self,observable:IObservable=None):
        self.__observable = observable

    def pour_Mixtral(self,utilisateur:str,salon:str,question:str):
        print(f"Question de {utilisateur} du salon {salon}: {question}")
        transaction_id = im.sqliteh.ajout_question(utilisateur, salon,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        reponse = ""
        try:
            reponse = im.interroge_mixtral(utilisateur, salon,question);
            print(f"Réponse de Mixtral \"{reponse}\"")
            reponse = reponse.json()["choices"][0]["message"]["content"]
            print(f"Voici la réponse: {reponse}")
            im.sqliteh.modification_reponse(utilisateur, salon, transaction_id,reponse)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
            im.sqliteh.remove_transaction(utilisateur, salon,transaction_id)
            reponse = None
        return reponse

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        reponse = self.pour_Mixtral(event.sender,room.display_name,msg)
        if reponse == None:
            reponse = "Une erreur s'est produite lors de l'interrogation de Mixtral"
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