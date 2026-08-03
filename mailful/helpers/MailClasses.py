from collections.abc import Sequence
from typing import List, Dict, Generic, TypeVar
import datetime

from dataclasses import dataclass, field

T = TypeVar("T")
@dataclass
class SendMailResponse(Generic[T]):
    success: bool = False

    provider: str = None
    data: T | None = None

@dataclass
class MailRecipient:
    Email: str
    Name: str

    def __str__(self):
        return self.Email

@dataclass
class MailAttachment(Generic[T]):
    filename: str
    content: bytes
    content_type: str | None = None
    content_disposition: str | None = None

    include_attachments: bool = False
    extra_provider_info: T | None = None

@dataclass
class BaseMailMessage:
    subject: str
    """The subject of the email."""
    text: str
    """The plaintext version of the email. Usually, email websites display HTML instead of text."""
    html: str | None = ""
    """The HTML version of the email. 
    
    Even if you had the HTML and majority of websites (Gmail, Outlook, etc) primarily show it..
    That doesn't mean you can ignore the text parameter, 
    as the text parameter is suited for the compatibility, reliability, and accessibility for clients that can't display HTML."""
    to: Sequence[MailRecipient | str] = field(default_factory=list)
    """The list of people to send the email to."""
    cc: Sequence[MailRecipient | str] = field(default_factory=list)
    """The list of people that receive a copy of the email."""
    bcc: Sequence[MailRecipient | str] = field(default_factory=list)
    """The list of people that receives a copy of the email, but they cannot see the list of people that the email was sent to using the "to" parameter."""

# NO FUCKING PARAMETERS (yet:3) LMAOO
@dataclass
class MailDraft(BaseMailMessage):
    from_email: str | None = None

@dataclass
class MailMessage(BaseMailMessage, Generic[T]):

    from_: MailRecipient | None = None
    """This property defines who/what sent this email."""
    timestamp: datetime.datetime | None = None
    """This property defines when this email was sent."""
    size: int | None = None
    """This property defines how big the email is."""

    in_reply_to: str | None = None
    """This property defines who the email is replying to. Can be None if the email wasn't a reply."""
    preview: str | None = None
    """This property defines the starting snippet of the email body."""
    updated_at: datetime.datetime | None = None
    """This property defines the time of the last update of the email."""
    headers: Dict[str, any] | None = None
    """This property defines the headers of the request."""
    attachments: Sequence[MailAttachment] | None = None
    """This property defines the files attached to this email."""

    raw_text: str | None = None,
    """This property defines the raw text of the email."""
    raw_html: str | None = None,
    """This property defines the raw html of the email."""

    references: Sequence[str] | None = None,
    """This property references related to the email."""
    in_depth: bool = False,
    """This property is here to see if the email was checked in depth or not."""
    extra_provider_info: T | None = None
    """This property is here if the email provider wants to add any additional information."""

    def __str__(self):
        text = self.preview.replace("\n", "")

        endwithdots = True
        if len(text) < 25:
            endwithdots = False

        return f"""<MailMessage object_preview:"{text[:25] + (".." if endwithdots else "")}"_timestamp:{self.timestamp}_from:"{self.from_}">"""

@dataclass
class HttpMailQuery:
    """For HTTP mail providers only."""

    limit: int = 50
    before: datetime.datetime | None = None
    after: datetime.datetime | None = None
    to: Sequence[MailRecipient | str] | None = field(default_factory=list)
    from_: Sequence[MailRecipient | str] | None = None
    ascending: bool = False
    subject: str | None = None
    labels: Sequence[str] | None = None
    include_spam: bool = False
    include_blocked: bool = False
    include_unauthenticated: bool = False
    include_trash: bool = False
    only_unread: bool = False
    in_depth: bool = False
    include_attachments: bool = False