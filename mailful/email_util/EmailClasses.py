from typing import Sequence, DefaultDict, List
from dataclasses import field
from ..helpers.MailClasses import MailRecipient
from ..errors.CommonErrors import MissingRequirementsToUseFeatureError
from .email_util_errors.EmailClassesErrors import EmailDraftfulFailedRemoveError

from io import FileIO
from importlib.util import find_spec

class EmailDraftful:
    def __init__(self, *, 
                 to: Sequence[MailRecipient | str] = [], 
                 cc: Sequence[MailRecipient | str] = [], 
                 bcc: Sequence[MailRecipient | str] = [], 
                 subject: str = "", 
                 text: str = "", 
                 html: str = ""):
        
        self.to: List[MailRecipient | str] = to or []
        self.cc: List[MailRecipient | str] = cc or []
        self.bcc: List[MailRecipient | str] = bcc or []
        
        self.subject: str = subject or ""
        self.text: str = text or ""
        self.html: str = html or ""

    def _helper_remove_recip(self, recip, classname):
        try:

            if isinstance(recip, (MailRecipient, str)):
                self.__getattribute__(classname).remove(recip)
                return
            
            if isinstance(recip, Sequence):
                
                for recipient in recip:
                    if isinstance(recipient, MailRecipient):
                        
                        self.__getattribute__(classname).remove(recipient)
                        
                        continue
    
                    if isinstance(recipient, str):
                        
                        self.__getattribute__(classname).remove(recipient)
                        
                        continue

        except ValueError as e:
            raise EmailDraftfulFailedRemoveError(f"Failed to remove {recip} from {classname}")
    
    def _helper_add_recip(self, recip, classname):
        if isinstance(recip, (MailRecipient, str)):
            getattr(self, classname).append(recip)
            return

        if isinstance(recip, Sequence):
            
            for recipient in recip:
                if isinstance(recipient, MailRecipient):
                    
                    self.__getattribute__(classname).append(recipient)
                    
                    continue

                if isinstance(recipient, str):
                    
                    self.__getattribute__(classname).append(recipient)
                    
                    continue
        
    def add_to(self, to: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_add_recip(
            to, "to"
        )
        
        return self

    def remove_to(self, to: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_remove_recip(
            to, "to"
        )

        return self
    
    def add_bcc(self, bcc: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_add_recip(
            bcc, "bcc"
        )
        
        return self

    def remove_bcc(self, bcc: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_remove_recip(
            bcc, "bcc"
        )

        return self
    
    def add_cc(self, cc: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_add_recip(
            cc, "cc"
        )
        
        return self

    def remove_cc(self, cc: Sequence[MailRecipient | str] | MailRecipient | str):
        self._helper_remove_recip(
            cc, "cc"
        )

        return self
    
    def add_text(self, text: str):
        
        self.text = f"{self.text}{text}"
        return self
    
    def set_text(self, text: str):
        
        self.text = text
        
        return self
    
    def add_html(self, html: str):
        
        self.html = f"{self.html}{html}"
        return self
    
    def set_html(self, html: str):
        
        self.html = html
        return self
    
    def set_subject(self, subject: str):
        
        self.subject = subject
        return self
    
    def add_subject(self, subject: str):
        
        self.subject = f"{self.subject}{subject}"
        return self
    
class EmailTemplate:
    requirements = [
        "jinja2"
    ]
    
    @classmethod
    def _has_requirements(cls):
        for module in cls.requirements:
            spec = find_spec(module)

            if spec == None:
                return False
        return True
    
    def __init__(self, source: FileIO | str):
        if not self._has_requirements():
            raise MissingRequirementsToUseFeatureError(
                f"""Missing requirements for feature: {self.__class__.__name__}.
                             You must install these packages with the command: pip install {" ".join(self.requirements)}.""",
                             
                             self.__class__.__name__
            )
            
        self.contents = ""
            
        if type(source) == FileIO:
            
            with source as f:
                self.contents = f.read()
        
        if type(source) == str:
            self.contents = source
                
        self.result = ""
        
    def set_template_text(self, new_text: str):
        self.contents = new_text
        
    def render(self, **kwargs): 
        
        import jinja2
        
        env = jinja2.Environment(autoescape=True)
        newTemplate = env.from_string(
            self.contents
        )
        
        self.result = newTemplate.render(**kwargs)
        return self.result

        
    def __str__(self):
        
        return self.result