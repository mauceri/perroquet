import logging
import os
from amicus_interfaces import IObserver, IObservable, IPlugin
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText
from .sqlite_handler import SQLiteHandler
from .interrogationMixtralAnyscale import InterrogationMixtral



logger = logging.getLogger(__name__)

    
class Perroquet(IObserver):
    def __init__(self,observable:IObservable=None,db_path:str=None):
        self.__observable = observable
        self.sqliteh = SQLiteHandler(db_path=os.path.join(db_path,"test_context.sqlite"))
        self.im = InterrogationMixtral(self.sqliteh.db_path)

    def pour_Mixtral(self,utilisateur:str,salon:str,question:str):
        print(f"Question de {utilisateur} du salon {salon}: {question}")
        transaction_id = self.im.sqliteh.ajout_question(utilisateur, salon,question).lastrowid
        print(f"L'id de la transaction pour la question {question} est {transaction_id}")
            
        reponse = ""
        try:
            reponse = self.im.interroge_mixtral(utilisateur, salon,question);
            logger.info(f"Réponse de Mixtral \"{reponse}\"")
            reponse = reponse.choices[0].message.content
            logger.info(f"Voici la réponse: {reponse}")
            self.im.sqliteh.modification_reponse(utilisateur, salon, transaction_id,reponse)
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Mixtral {e}")
            self.im.sqliteh.remove_transaction(utilisateur, salon,transaction_id)
            reponse = None
        return reponse

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        logging.info(f"************ ANY_SCALE_API_KEY={os.getenv('ANY_SCALE_API_KEY')}")
        reponse = self.pour_Mixtral(event.sender,room.display_name,msg)
        if reponse == None:
            reponse = "Une erreur s'est produite lors de l'interrogation de Mixtral"
        await self.__observable.notify(room, event, "Coco a dit : "+reponse, None, None)

    def prefix(self):
        return "!coco"
    
class Plugin(IPlugin):
    def __init__(self,observable:IObservable,path:str):
        super().__init__(observable,path)
        self.observable = observable
        self.perroquet = Perroquet(self.observable,path)
        logger.info(f"********************** Observateur créé {self.perroquet.prefix()}")
        
    def start(self):
        logger.info(f"********************** Inscripton de {self.perroquet.prefix()}")
        self.observable.subscribe(self.perroquet)

    async def stop(self):
        self.observable.unsubscribe(self.perroquet)