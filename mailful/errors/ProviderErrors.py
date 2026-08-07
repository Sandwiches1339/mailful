class ProviderNotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


    pass

class MissingRequirementsToRunProviderError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        
class ProviderDoesNotHaveFeatureError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Provider does not have {message} feature.")


class MissingParametersError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    pass

class ProviderRateLimitedError(Exception):
    def __init__(self, provider):
        self.provider = provider

    pass