from typing import Dict, Literal, Type, overload, Union, Any

from .providers import *
from .errors.ProviderErrors import ProviderNotFoundError
from .abstractbaseclass.ProviderClass import BaseProvider

from .providers.SMTP import SMTPProvider

RegisteredProviders = Literal[
    "SMTPProvider",
    "AgentMailProvider"
]

reg: Dict[str, type[BaseProvider]] = {}

def add_list(name: str, provider: BaseProvider):
    reg[name] = provider
    
@overload
def get_provider_quick(name: Literal["smtp"]) -> type[SMTPProvider]: ...

@overload
def get_provider_quick(name: Literal["agentmail"]) -> type[AgentMailProvider]: ...


def get_provider_quick(name: str) -> BaseProvider:
    match name.lower():
        case "agentmail":
            return AgentMailProvider

        case "smtp":
            return SMTPProvider

        case _:
            raise ProviderNotFoundError(
                f"Provider named {name} not found!"
            )