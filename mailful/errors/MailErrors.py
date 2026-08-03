class MailSendError(Exception):

    def __init__(self, provider: str, error: any):
        self.provider = provider
        self.error = error
    
    pass

