from ..abstractbaseclass.ProviderClass import BaseProvider
from ..errors.MailErrors import MailSendError
from ..errors.ProviderErrors import MissingParametersError, ProviderRateLimitedError
from ..helpers.MailClasses import MailRecipient, MailDraft, MailMessage, MailAttachment, SendMailResponse
from importlib.util import find_spec
from typing import TYPE_CHECKING, Sequence, List, Any, Dict
from dataclasses import dataclass
import asyncio
import time

if TYPE_CHECKING:
    from aiosmtplib import SMTPSenderRefused

@dataclass
class SMTPMailResponse:
    failed_recipients: List[str]

class SMTPProvider(BaseProvider):

    requirements: Sequence[str] = [
        "email", "aiosmtplib", "certifi"
    ]
    
    flags: Dict[str, bool] = {
        "websockets": False
    }

    async def _update_connection(self):
        
        if not self.client.is_connected:
            await self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                tls_context=self.certificate,
                
                **self.extra_args
            )
            
            self._log("Reconnected to SMTP server.")
            
    def _close_connection(self):
        if self.client.is_connected:
            asyncio.run(self.client.quit())

    @classmethod
    def _has_requirements(cls):
        for module in cls.requirements:
            spec = find_spec(module)

            if spec == None:
                return False
        return True

    def _log(self, *args):
        if self.verbose:
            print("[SMTPailful]", *args)

    def __init__(self, host, port=587, username=None, password=None, owner: Any | None = None, verbose: bool = False, use_mozilla_certificate: bool = True, **kwargs):
        import aiosmtplib
        self.certificate = None
        self.use_mozilla_certificate = use_mozilla_certificate
        
        if self.use_mozilla_certificate:
            import ssl, certifi

            self.certificate = ssl.create_default_context(cafile=certifi.where())
            
        self.owner = owner or None
        
        self.host = host
        self.port = port
        
        self.username = username
        self.password = password
        self.extra_args = kwargs

        self.client = aiosmtplib.SMTP(tls_context=self.certificate, hostname=self.host, port=self.port, username=self.username, password=self.password, **kwargs)
        self.verbose = verbose

    async def send(self, maildraft) -> SendMailResponse[SMTPMailResponse]:
        """
Send mail to recipients.

:param maildraft: The MailDraft (Not to be confused with EmailDraftful) object containing sender, recipients, subject, and content.
:returns: The sent mail response.
:raises MailSendError: If the SMTP failed to send the mail.
"""

        if not self.host or not self.port: return

        import aiosmtplib
        from email.message import EmailMessage

        try:

            # Keep Connection Alive.
            await self._update_connection()
            last = time.time()
            
            client = self.client
            
            # EmailBuilder. Maybe I should support this in v0.0.1dev4
            # I did.
            msg = EmailMessage()
            msg["From"] = maildraft.from_email or self.username
            msg["To"] = ", ".join(
                recip.email if isinstance(recip, MailRecipient) else recip
                for recip in maildraft.to
            )


            if maildraft.cc:
                msg["Cc"] = ", ".join(
                    recip.email if isinstance(recip, MailRecipient) else recip
                    for recip in maildraft.cc
                )


            if maildraft.bcc:
                msg["Bcc"] = ", ".join(
                    recip.email if isinstance(recip, MailRecipient) else recip
                    for recip in maildraft.bcc
                )


            msg["Subject"] = maildraft.subject
            if maildraft.text:
                msg.set_content(maildraft.text)

            if maildraft.html:
                if maildraft.text:
                    msg.add_alternative(maildraft.html, subtype="html")
                else:
                    msg.set_content(maildraft.html, subtype="html")

            result = await client.send_message(
                msg
            )

            response = SMTPMailResponse(
                result
            )

            now = time.time()

            self._log(f"""Finished sending email SMTP_SUBJECT"{maildraft.subject}"_TO_"{maildraft.to}". Took {float(now - last):.4f}s""")
            
            SMR = SendMailResponse(
                success=True,
                provider="smtp",

                data=response
            )
            
            SMR.data
            
            return SMR

        except aiosmtplib.SMTPSenderRefused as e:
            
            raise MailSendError(
                provider="smtp",
                message=str(e),
            )

    
    async def receive(self, HttpMailQuery)-> Sequence[MailMessage]:
        """SMTP doesn't support this "shit", L(AUGHING)O(UT)L(OUD)."""

        if not self.client: return