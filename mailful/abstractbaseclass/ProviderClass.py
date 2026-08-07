from abc import ABC, abstractmethod
from typing import List, Sequence, TypeVar, Generic, Self, Callable, Type, Literal, Dict
from ..helpers.MailClasses import MailDraft, MailRecipient, HttpMailQuery, SendMailResponse

R = TypeVar("P")
EventInfo = TypeVar("EventInfo")

Features = ["websocket"]
FeaturesType = Literal[*Features]

"""Base mail provider class for sending/receiving mail."""
class BaseProvider(Generic[R, EventInfo], ABC):

    requirements: Sequence[str]
    
    flags: Dict[str, bool] = {
        ...
    }
        
    
    def __init__(self, owner, *args, **kwargs):
        self.owner = owner
        
        ...
        
    def _has_flag(self, flag: str) -> bool:
        """Check if it has flag available."""
       
        if self.flags:
            key = self.flags.get(flag)
            
            if not key:
                return False
            
            return True
        
        return False
        
    
    """Does user have prerequisites to run this provider?"""
    def _has_requirements() -> bool:
        ...

    """Send a message using said provider."""
    async def send(self, maildraft: MailDraft) -> SendMailResponse[R]:
        ...

    """Receive a message using said provider. HTTP ONLY."""
    async def receive(self, HttpMailQuery: HttpMailQuery):
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support receiving mail."
        )
        
        
    """Emit events from provider."""
    async def _emit(self, eventname: str, eventdata: Type[EventInfo]):
        self.owner.emit(
            eventname,
            eventdata
        )