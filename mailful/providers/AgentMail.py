from ..abstractbaseclass.ProviderClass import BaseProvider
from ..errors.MailErrors import MailSendError
from ..errors.ProviderErrors import MissingParametersError, ProviderRateLimitedError
from ..helpers.MailClasses import MailRecipient, MailDraft, MailMessage, MailAttachment, SendMailResponse
from importlib.util import find_spec
from traceback import print_exc
from typing import TYPE_CHECKING, Sequence, TypeVar, cast
from dataclasses import dataclass
import aiohttp
import asyncio
import warnings
import time

# hello. heres some paramaters.
# i dont know why i added them, but yeah. hardcoded.
# people will say this is mailbridge.
# sorry man, i just found out halfway development about it.
# you should try mailbridge though, its awesomestness.

MAX_LIMIT_PAGE = 100
MAX_ATTEMPTS = 5

if TYPE_CHECKING:
    from agentmail.messages import SendMessageResponse

@dataclass
class AgentMailAdditionalInfo:
    inbox_id: str | None = None
    thread_id: str | None = None
    message_id: str | None = None


@dataclass
class AgentMailAttachmentInfo:
    attachment_id: int | None = None
    download_url: str | None = None

T = TypeVar("T")

class AgentMailProvider(BaseProvider):

    requirements: Sequence[str] = [
        "agentmail"
    ]

    @classmethod
    def _has_requirements(cls):
        for module in cls.requirements:
            spec = find_spec(module)

            if spec == None:
                return False
        return True

    def _log(self, *args):
        if self.verbose:
            print("[AgentMailful]", *args)

    def __init__(self, api_key: str, inbox_id: str, verbose: bool = False):
        from agentmail import AsyncAgentMail

        self.verbose = verbose

        self.api_key = api_key
        self.client = AsyncAgentMail(api_key=api_key)
        self.inbox_id = inbox_id
        
        self._log("Initialized AgentMailful")
        
        
        

    async def send(self, maildraft) -> SendMailResponse[None]:
        """
Send mail to recipients.

:param maildraft: The MailDraft object containing sender, recipients, subject, and content.
:returns: The sent mail message response.
:raises MailSendError: If the AgentMail API failed to send the mail.
"""
        
        if not self.client: return

        import agentmail, agentmail.core
        self._log("Executing method send")

        try:
            inboxes = self.client.inboxes

            messages = inboxes.messages

            last = time.time()


            # Im sorry, I gotta do what i gotta do man. -_-
            result = await messages.send(inbox_id=self.inbox_id, 
                to=[recip.email if isinstance(recip, MailRecipient) else recip for recip in maildraft.to] if isinstance(maildraft.to, list) else [maildraft.to.email],
                cc=[recip.email if isinstance(recip, MailRecipient) else recip for recip in maildraft.cc] if isinstance(maildraft.cc, list) else [maildraft.cc.email],
                bcc=[recip.email if isinstance(recip, MailRecipient) else recip for recip in maildraft.bcc] if isinstance(maildraft.bcc, list) else [maildraft.bcc.email],
                subject=maildraft.subject,
                text=maildraft.text,
                html=maildraft.html)
            
            now = time.time()

            self._log(f"Finished sending email AGENTMAIL_{result.message_id}. Took {float(now - last):.4f}s")

            mailresponse = SendMailResponse(
                success=True,
                provider="agentmail",

                data=result
            )

            return mailresponse

        except agentmail.core.ApiError as e:
            
            raise MailSendError(
                provider="agentmail",
                message=str(e),
            )


    async def _request(self, method, *args, **kwargs):
        import agentmail.core as AgentMailCore

        for attempt in range(MAX_ATTEMPTS):

            try:
                print("start")
                result = await method(*args, **kwargs)
                print(result)
                
                return result

            except AgentMailCore.ApiError as e:
                if e.status_code == 429:

                    RetryAfter = int(e.headers.get("Retry-After", 1)) ** attempt

                    warnings.warn(f"Dude, we're being rate limited!! Retrying after {RetryAfter} seconds.")

                    await asyncio.sleep(RetryAfter)

                else:

                    raise

        raise ProviderRateLimitedError(
            provider="agentmail"
        )


    async def _parse_attachments(self, query, messages, message):
        import agentmail

        attachments = []
        
        if message.attachments != None:
        
            for attachment in message.attachments:
                newAttachment = MailAttachment(
                    filename=attachment.filename,
                    content_type=attachment.content_type,
                    content_disposition=attachment.content_disposition,
                )
        
                newAgentMailStuff = AgentMailAttachmentInfo(attachment_id=attachment.attachment_id)
        
                if query.include_attachments:
                    message: agentmail.Message
            
                    attachmentInDepth = await self._request(messages.get_attachment,
                        message.inbox_id,
                        message.message_id,
                        attachment.attachment_id
                    )
        
                    newAgentMailStuff.download_url = attachmentInDepth.download_url
            
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachmentInDepth.download_url) as response:
                                content = await response.read()
                        
                                newAttachment.content = content

                    except aiohttp.ClientError as e:
                        newAttachment.content = None

                        print(f"Failed to download attachment {attachment.attachment_id}, {e}")

                    except Exception as e:
                        newAttachment.content = None

                        print(f"Attachment error for {attachment.attachment_id}, {e}")

                newAttachment.extra_provider_info = newAgentMailStuff

        return attachments

    
    async def receive(self, HttpMailQuery)-> Sequence[MailMessage]:
        """Receive mail from inbox. 
        (NOTE: AgentMail can read up to 100 messages. Pagination required.)
        (REALLY BAD NOTE: AgentMail uses token based pagination, which means for 500 mails, You have to iterate 5 pages, which means 5 requests.)
        (It's worse for in_depth mode, by the way. 500 mails, 5 pages, 505 requests. Every mail needs to be requested for its full Email view. Caching? Maybs.)
                
        :param HttpMailQuery: HttpMailQuery for clean and object oriented projects. You can use my evil brother receive_quick if you dont wanna make objects all day long!"""

        if not self.client: return

        query = HttpMailQuery

        # Fuckers
        if query is None:
            raise MissingParametersError("You are missing the entire HttpMailQuery object.")
            return

        # Absolute Fuckery right here man
        if query.limit is None:
            raise MissingParametersError("limit parameter is None. How do you even achieve this? I already put a default if you didnt set limit to 50. Did you turn this into None? Really dude?")
            return

        # Missing req? Sorry, You have to face the error yourself.
        import agentmail, agentmail.core

        try:
            
            self._log("Executing method receive")
            
            inboxes = self.client.inboxes
        
            messages = inboxes.messages

            # limit to MAX_LIMIT_PAGE which is ontop of the script!
            pages = round(query.limit / MAX_LIMIT_PAGE)
            amountLeft = query.limit
            count = 0
            token = None

            allMail = []

            
            # Start iterating..
            while amountLeft > 0:
                currentLimit = min(amountLeft, MAX_LIMIT_PAGE)

                # Heckoalot text right here, ye.
                currentPage = await self._request(messages.list, 
                                            self.inbox_id, 
                                            limit=currentLimit,
                                            page_token=token,
                                            labels=query.labels,
                                            before=query.before,
                                            after=query.after,
                                            include_spam=query.include_spam,
                                            include_blocked=query.include_blocked,
                                            include_trash=query.include_unauthenticated,
                                            include_unauthenticated=query.include_unauthenticated,
                                            subject=query.subject,
                                            to=[str(email) for email in query.to],
                                            from_=query.from_,
                                            ascending=query.ascending)

                for message in currentPage.messages:
                    last = time.time()

                    message: agentmail.MessageItem

                    text = None
                    html = None

                    rawtext = None
                    rawhtml = None

                    if query.in_depth:
                        message = await self._request(messages.get, message.inbox_id, message.message_id)

                        text = message.extracted_text
                        html = message.extracted_html

                        rawtext = message.text
                        rawhtml = message.html
                    

                    mailMessage = MailMessage(
                        subject=message.subject,
                        text=text,
                        raw_text=rawtext,
                        html=html,
                        raw_html=rawhtml,
                        from_=message.from_,
                        timestamp=message.timestamp,
                        cc=message.cc,
                        bcc=message.bcc,
                        headers=message.headers,
                        references=message.references,
                        preview=message.preview,
                        in_depth=query.in_depth,
                        to=message.to,
                        in_reply_to=message.in_reply_to
                    )

                    mailMessage.extra_provider_info = AgentMailAdditionalInfo(
                        message.inbox_id,
                        message.thread_id,
                        message.message_id
                    )

                    mailMessage.attachments = await self._parse_attachments(query, messages, message)

                    
                    now = time.time()
                    self._log(f"Finished parsing email AGENTMAIL_{message.message_id}. Took {float(now - last):.4f}s")

                    allMail.append(mailMessage)

                amountLeft -= len(currentPage.messages)
                token = currentPage.next_page_token
            
            return allMail

        except agentmail.core.ApiError as e:
                    
            raise MailSendError(
                provider="agentmail",
                message=str(e),
            )