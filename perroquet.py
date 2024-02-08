import logging
from amicus_bot.interfaces import IObserver, IObservable, IPlugin
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText
from amicus_bot.callbacks import Callbacks


logger = logging.getLogger(__name__)

class Echo(IObserver):
    def __init__(self,observable:Callbacks=None):
        self.observable =observable

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        await self.observable.notify(room, event, f"L'utilisateur {event.sender} a écrit {msg} depuis le salon {room.name}")

    def prefix(self):
        return "!echo"

    

    
class Perroquet(IObserver):
    def __init__(self,observable:Callbacks=None):
        self.observable =observable

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        await self.observable.notify(room, event, f"L'utilisateur {event.sender} a écrit \"{msg}\" depuis le salon {room.name}")

    def prefix(self):
        return "!coco"
    
class Plugin(IPlugin):
    def __init__(self,observable:IObservable):
        self.observable = observable
        self.perroquet = Perroquet(observable)
        logger.info(f"********************** Observateur créé {self.perroquet.prefix()}")
        
    def start(self):
        logger.info(f"********************** Inscripton de {self.perroquet.prefix()}")
        self.observable.subscribe(self.perroquet)

    async def stop(self):
        pass