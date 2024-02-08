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

    
class Ping(IObserver):
    def __init__(self,observable:Callbacks=None):
        self.observable =observable

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        await self.observable.notify(room, event, f"L'utilisateur {event.sender} a écrit {msg} depuis le salon {room.name}")

    def prefix(self):
        return "!ping"
    
class Baba(IObserver):
    def __init__(self,observable:Callbacks=None):
        self.observable =observable

    async def notify(self,room:MatrixRoom, event:RoomMessageText, msg:str):
        logger.info(f"***************************** L'utilisateur {event.sender} a écrit {msg} depuis ls salon {room.name}")
        await self.observable.notify(room, event, f"L'utilisateur {event.sender} a écrit \"{msg}\" depuis le salon {room.name}")

    def prefix(self):
        return "!baba"
    
class Plugin(IPlugin):
    def __init__(self,observable:IObservable):
        self.observable = observable
        self.echo = Echo(observable)
        logger.info(f"********************** Observateur créé {self.echo.prefix()}")
        self.ping = Ping(observable)
        logger.info(f"********************** Observateur créé {self.ping.prefix()}")
        self.baba = Baba(observable)
        logger.info(f"********************** Observateur créé {self.baba.prefix()}")
        
    def start(self):
        logger.info(f"********************** Inscripton de {self.echo.prefix()}")
        self.observable.subscribe(self.echo)
        logger.info(f"********************** Inscripton de {self.ping.prefix()}")
        self.observable.subscribe(self.ping)
        logger.info(f"********************** Inscripton de {self.baba.prefix()}")
        self.observable.subscribe(self.baba)

    async def stop(self):
        pass