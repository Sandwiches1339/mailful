class MissingRequirementsToUseFeatureError(Exception):
    def __init__(self, message: str, feature: str):
        self.feature = feature
        
        super().__init__(message)