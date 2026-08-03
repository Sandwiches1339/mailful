from .UnifiedMailer import MailfulClient
from .ProviderList import get_provider_quick
from . import providers, errors, email_util
from .helpers.MailClasses import (
    MailMessage,
    MailDraft,
    MailRecipient,
    MailAttachment,
    HttpMailQuery
)
from .email_util.EmailClasses import EmailDraftful

__all__ = [
    "MailfulClient",
    "get_provider_quick",
    "providers",
    "errors",
    "MailMessage",
    "MailDraft",
    "MailRecipient",
    "MailAttachment",
    "HttpMailQuery",
    "EmailDraftful",
    "email_util"
]
