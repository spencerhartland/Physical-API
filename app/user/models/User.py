from ...common import Error

# Dictionary keys
usernameKey = "username"
userIDKey = "userID"
displayNameKey = "displayName"
biographyKey = "biography"
followersKey = "followers"
followingKey = "following"
featuredKey = "featured"
collectionKey = "collection"
postsKey = "posts"

# An object representing a user.
#
# Attributes:
#    - userID: The unique user identifier assigned to the user by Apple.
#    - username: The unique username chosen by the user.
#    - displayName: The user's chosen display name.
#    - biography: The user's biography.
#    - followers: The unique user identifiers of the user's followers.
#    - following: The unique user identifiers of the user's followed accounts.
#    - featured: The Music Item ID of the user's featured Music Item.
#    - collection: The unique identifier of the user's collection.
#    - posts: The unique identifiers of the user's authored posts.
class User:
    def __init__(self, userDict):
        try:
            self.username = userDict[usernameKey]
            self.userID = userDict[userIDKey]
            self.displayName = userDict[displayNameKey]
            self.biography = userDict[biographyKey]
            self.followers = userDict[followersKey]
            self.following = userDict[followingKey]
            self.featured = userDict[featuredKey]
            self.collection = userDict[collectionKey]
            self.posts = userDict[postsKey]
        except:
            raise Error.AttributeNotFoundError()
