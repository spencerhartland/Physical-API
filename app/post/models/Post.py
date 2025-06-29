from ...common import Error

# Attribute keys
postIDKey = "postID"
authorKey = "author"
timestampKey = "timestamp"
captionKey = "caption"

# The abstract superclass for all posts.
#
# Attributes:
#    - id: The unique identifier for the post.
#    - author: The unique identifier for the author of the post.
#    - timestamp: The date / time that the post was published, represented as seconds since epoch.
#    - caption: The post's caption.
class Post:
    def __init__(self, postDict):
        self.id = postDict[postIDKey]
        self.author = postDict[authorKey]
        self.timestamp = postDict[timestampKey]
        self.caption = postDict[captionKey]