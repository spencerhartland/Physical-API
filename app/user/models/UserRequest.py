from ...common import Error

# ID types
idTypeUsername = "username"
idTypeUserID = "userID"

# An object containing information needed to request a user's account.
class UserRequest:
    def __init__(self, idType, identifier):
    
        if idType == idTypeUsername or idType == idTypeUserID:
            self.idType = idType
        else:
            raise InvalidIDTypeError()
            
        self.identifier = identifier

class InvalidIDTypeError(Exception):
    def __init__(self):
        super().__init__("The specified ID type is invalid.")
