class ProviderNotFoundError:

    pass

class MissingRequirementsToRunProviderError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class MissingParametersError:
    pass

class ProviderRateLimitedError:
    def __init__(self, provider):
        self.provider = provider

    pass