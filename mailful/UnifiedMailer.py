from .abstractbaseclass.ProviderClass import BaseProvider
from .errors.ProviderErrors import ProviderNotFoundError, MissingRequirementsToRunProviderError
from .ProviderList import reg, RegisteredProviders
from .providers import *

#smtp doesnt work for imports 4 some reason looll
from .providers.SMTP import *
from typing import Literal, TypeVar, Generic, Type, Sequence, overload, Union
from .helpers.MailClasses import MailRecipient, MailDraft, HttpMailQuery
from dataclasses import field
from typing import List, Any, cast
import warnings, asyncio
import datetime

P = TypeVar("P", bound="BaseProvider")
T = TypeVar("T")

# v0.0.2 will have more documentation!


"""I have provided providers if you want to, this is only a method for getting providers quick without importing classes."""
class MailfulClient(Generic[P, T]):
    """Main client that sends and receives mail. Acts as a middleman for the mail providers.
    
    Example:
        >>> from mailful import MailfulClient, get_provider_quick
>>> client = MailfulClient(
>>>     provider=get_provider_quick("agentmail"), 
>>>     api_key="am_xx_xxxxxxxxxxxxxxxxxx",
>>>     inbox_id="sandwichesarethebestmeow@agentmail.to" 
>>>     # Due to the Mailful being agnostic, you can simply swap your providers using the change_provider() method!
>>>     # Now, you can swap your providers without changing ANY code!* (Provider Specific Features not covered)
>>> )
>>> 
>>> # You can go do mailful.provider.send or use mailful.send OR mailful.send_quick! All occassions are welcome!
>>> client.send_quick_sync(
>>>     subject="Mailful!!",
>>>     html="<p>This is email sent from the Mailful package! Do you see how easy it is?</p>",
>>>     text="Forward any bugs to the email below! Or do a pull request on the github!",
>>>     to=["sandwichesarethebestmeow@gmail.com"]
>>> )

    """

    def _boiler_provider_set(self, provider: Type[P], *args, verbose: bool = False, **kwargs):
        
        if isinstance(provider, str):
                
            tryToGetProvider = reg.get(provider)
                
            if not tryToGetProvider:
                raise ProviderNotFoundError

            if not tryToGetProvider._has_requirements():
                raise MissingRequirementsToRunProviderError(f"""Missing requirements for provider: {tryToGetProvider.__name__}.
                                             You must install these packages: pip install {" ".join(tryToGetProvider.requirements)}.""")
                
            self.provider = tryToGetProvider(*args, **kwargs, verbose=verbose)

            return

        if not provider._has_requirements():
             raise MissingRequirementsToRunProviderError(f"""Missing requirements for provider: {provider.__name__}.
                             You must install these packages with the command: pip install {" ".join(provider.requirements)}.""")
        
        self.provider = provider(*args, **kwargs, verbose=verbose)
        

    """
    @overload
    def __init__(self, provider: Type[SMTPProvider], *, host: str, port: int = 587, username: str | None = None): ...

    @overload
    def __init__(self, provider: Type[AgentMailProvider], *, api_key: str): ...

    @overload
    def change_provider(self, provider: Type[SMTPProvider], *, host: str, port: int = 587, username: str | None = None): ...

    @overload
    def change_provider(self, provider: Type[AgentMailProvider], *, api_key: str): ..."""

    def __init__(self, provider: Type[P], *args, verbose: bool = False, **kwargs):

        self._boiler_provider_set(provider, *args, **kwargs, verbose=verbose)
        
        self.provider : P
        self.verbose = verbose

    def change_provider(self, provider: Type[P] | None = None, *args, verbose: bool = False, **kwargs):
        """
Swap to a different provider, or reinitialize the same provider if no provider is supplied as an argument.
For example, if you were using AgentMail, you would use the AgentMailProvider, seen below.

Example:
>>> from mailful import MailfulClient, get_provider_quick
>>>
>>> client = MailfulClient(
>>>     provider=get_provider_quick("agentmail"), 
>>>     api_key="am_xx_xxxxxxxxxxxxxxxxxx",
>>>     inbox_id="sandwichesarethebestmeow@agentmail.to" 
>>> )

----

Now, doing change_provider to a MailfulClient object will reinitialize it with the new provider, 
so if later you want to switch to SMTP, You can.
        
Example:
>>> client.change_provider(
>>>     provider=get_provider_quick("smtp"),
>>>     host="example.com",
>>>     port=0000,
>>>     username="sandwichesarethebest",
>>>     password="meow",

>>>     use_tls=True,
>>>     use_ssl=True
>>> )

>>> client.send_quick_sync(
>>>     subject="Mailful!!",
>>>     html="<p>This is email sent from the Mailful package! Do you see how easy it is?</p>",
>>>     text="Forward any bugs to the email below! Or do a pull request on the github!",
>>>     to=["sandwichesarethebestmeow@gmail.com"]
>>> )


The rest of your code won't need to change, since the functions will stay the same!
        
        """
        if not provider:
             self._boiler_provider_set(self.provider.__class__, *args, **kwargs, verbose=verbose)
             return
        
        self.provider : P
        self._boiler_provider_set(provider, *args, **kwargs, verbose=verbose)

        self.verbose = verbose

    async def send(self, maildraft: MailDraft) -> SendMailResponse[T]:
            """
            Send mail to recipients.

            :param maildraft: The MailDraft object containing sender, recipients, subject, and content.
            :returns: The sent mail message response.
            :raises MailSendError: If the AgentMail API failed to send the mail.
            """
            
            result = await self.provider.send(maildraft)
    
            return result

    def send_sync(self, maildraft: MailDraft) -> SendMailResponse:
                """
                Send mail to recipients synchronously.
    
                :param maildraft: The MailDraft object containing sender, recipients, subject, and content.
                :returns: The sent mail message response.
                :raises MailSendError: If the AgentMail API failed to send the mail.
                """
                
                result = asyncio.run(self.provider.send(maildraft))
                result: SendMailResponse[T]
        
                return result

    def send_quick_sync(self,
            *,
            to: Sequence[MailRecipient | str],
            subject: str,
            text: str,
            html: str | None = "",
            cc: Sequence[MailRecipient | str] | None = [],
            bcc: Sequence[MailRecipient | str] | None = []
        ) -> SendMailResponse[T]:
            """
            Send mail synchronously without manually creating a MailDraft object.
    
            :param subject: The subject of the mail.
            :param text: The text content of the mail.
            :param html: Optional HTML content.
            :param to: Recipients.
            :param cc: Carbon copy recipients.
            :param bcc: Blind carbon copy recipients.
            """
    
            if not to:
                raise ValueError("At least one recipient is required.")
    
            message = MailDraft(
                subject=subject,
                text=text,
                html=html,
                cc=cc,
                bcc=bcc,
                to=to
            )
    
            return asyncio.run(self.provider.send(message))

    async def send_quick(self,
        *,
        to: Sequence[MailRecipient | str],
        subject: str,
        text: str,
        html: str | None = "",
        cc: Sequence[MailRecipient | str] | None = [],
        bcc: Sequence[MailRecipient | str] | None = []
    ) -> SendMailResponse[T]:
        """
        Send mail without manually creating a MailDraft object.

        :param subject: The subject of the mail.
        :param text: The text content of the mail.
        :param html: Optional HTML content.
        :param to: Recipients.
        :param cc: Carbon copy recipients.
        :param bcc: Blind carbon copy recipients.
        """

        if not to:
            raise ValueError("At least one recipient is required.")

        message = MailDraft(
            subject=subject,
            text=text,
            html=html,
            cc=cc,
            bcc=bcc,
            to=to
        )

        return await self.provider.send(message)

    async def fetch(self,
            HttpMailQuery: HttpMailQuery
        ):
            """
            Fetch mail, only works on HTTP mail services, SMTP not supported.
    
            :param HttpMailQuery: The query that will be used to filter/specify the query.
            """
    
            if not HttpMailQuery:
                raise ValueError("HttpMailQuery is missing.")
    
            return await self.provider.receive(HttpMailQuery)

    def fetch_sync(self,
                HttpMailQuery: HttpMailQuery
            ):
                """
                Fetch mail synchronously, only works on HTTP mail services, SMTP not supported.
        
                :param HttpMailQuery: The query that will be used to filter/specify the query.
                """
        
                if not HttpMailQuery:
                    raise ValueError("HttpMailQuery is missing.")
        
                return asyncio.run(self.provider.receive(HttpMailQuery))

    def fetch_quick_sync(self,
                    limit: int = 50,
                    before: datetime.datetime | None = None,
                    after: datetime.datetime | None = None,
                    to: Sequence[MailRecipient | str] | None = field(default_factory=list),
                    from_: Sequence[MailRecipient | str] | None = None,
                    ascending: bool = False,
                    subject: str | None = None,
                    labels: Sequence[str] | None = None,
                    include_spam: bool = False,
                    include_blocked: bool = False,
                    include_unauthenticated: bool = False,
                    include_trash: bool = False,
                    only_unread: bool = False,
                    in_depth: bool = False,
                    include_attachments: bool = False,
                    **kwargs
                ):
                    """
                    Fetch mail synchronously, really quickly, only works on HTTP mail services, SMTP not supported.
                    """
                    if not limit:
                        raise ValueError("Limit parameter is missing.")

                    if not to:
                        raise ValueError("To paramater is missing.")

                    httpMailQuery = HttpMailQuery(
                        limit,
                        before,
                        after,
                        to,
                        from_,
                        ascending,
                        subject,
                        labels,
                        include_spam,
                        include_blocked,
                        include_unauthenticated,
                        include_trash,
                        only_unread,
                        in_depth,
                        include_attachments
                    )
            
                    return asyncio.run(self.provider.receive(httpMailQuery))

    async def fetch_quick(self,
                        limit: int = 50,
                        before: datetime.datetime | None = None,
                        after: datetime.datetime | None = None,
                        to: Sequence[MailRecipient | str] = [],
                        from_: Sequence[MailRecipient | str] = [],
                        ascending: bool = False,
                        subject: str | None = None,
                        labels: Sequence[str] | None = None,
                        include_spam: bool = False,
                        include_blocked: bool = False,
                        include_unauthenticated: bool = False,
                        include_trash: bool = False,
                        only_unread: bool = False,
                        in_depth: bool = False,
                        include_attachments: bool = False,
                        **kwargs
                    ):
                        """
                        Fetch mail, really quickly, only works on HTTP mail services, SMTP not supported.
                        """
                
                        if not limit:
                            raise ValueError("Limit parameter is missing.")

                        httpMailQuery = HttpMailQuery(
                            limit,
                            before,
                            after,
                            to,
                            from_,
                            ascending,
                            subject,
                            labels,
                            include_spam,
                            include_blocked,
                            include_unauthenticated,
                            include_trash,
                            only_unread,
                            in_depth,
                            include_attachments
                        )
                
                        return await self.provider.receive(httpMailQuery)