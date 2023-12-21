from ...common import Error

# Dictionary keys
userIDKey = "userID"

# An object representing a user ID
class UserID:
    def __init__(self, userIDDict):
    
        # Get user ID from dictionary
        try:
            self.rawValue = userIDDict[userIDKey]
        except:
            raise Error.AttributeNotFoundError(userIDKey)
