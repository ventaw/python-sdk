
class VentawError(Exception):
    pass

class APIError(VentawError):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class AuthenticationError(APIError):
    pass

class APIConnectionError(VentawError):
    pass
