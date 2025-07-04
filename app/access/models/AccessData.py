from ...common import Error

class AccessData:
    def __init__(self, accessToken: str, refreshToken: str):
        self.accessToken = accessToken
        self.refreshToken = refreshToken

    def json(self) -> dict:
        return {
            "accessToken": self.accessToken,
            "refreshToken": self.refreshToken
        }