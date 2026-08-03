from abc import ABC, abstractmethod
from typing import List, Sequence, TypeVar, Generic, Self
from ..helpers.MailClasses import MailDraft, MailRecipient, HttpMailQuery, SendMailResponse

R = TypeVar("P")

"""Base mail provider class for sending/receiving mail."""
class BaseProvider(Generic[R], ABC):

    requirements: Sequence[str]
    
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
            