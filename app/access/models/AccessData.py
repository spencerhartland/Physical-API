from ...common import Error

class AccessData:
    def __init__(self, accessToken: str, refreshToken: str):
        self.accessToken = accessToken
        self.refreshToken = refreshToken