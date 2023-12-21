from ...common import Error

# Dictionary keys
userIDKey = "userID"

# An object representing a user ID
class UserID:
    def __init__(self, userIDDict):
    
        # Get user ID from dictionary
        try:
            userID = userIDDict[userIDKey]
        except:
            raise Error.AttributeNotFoundError(userIDKey)
            
        # Save reference to the user ID
        self.rawValue = userID
