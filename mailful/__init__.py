from .UnifiedMailer import MailfulClient
from .helpers.MailClasses import MailMessage
from . import providers
from . import errors
from .ProviderList import get_provider_quick
from .helpers.MailClasses import (
    MailMessage,
    MailDraft,
    MailRecipient,
    MailAttachment,
    HttpMailQuery
)

__all__ = [
    "MailfulClient",
    "providers",
    "errors",
    "MailMessage",
    "get_provider_quick",
    "MailClasses"
]

