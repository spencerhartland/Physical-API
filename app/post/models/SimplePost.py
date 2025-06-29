from ...common import Error
import Post

# Attribute keys
songURLKey = "songURL"
mediaIDKey = "mediaID"

# A simple social post with a caption and content. The post's content may be 
# either a song from Apple Music or an item from the user's collection.
#
# Attributes:
#    - id: The unique identifier for the post.
#    - author: The unique identifier for the author of the post.
#    - timestamp: The date / time that the post was published, represented as seconds since epoch.
#    - caption: The post's caption.
#    - songURL: The song's Apple Music URL, if the post contains a song.
#    - mediaID: The unique identifier of an item in the user's collection, if the post contains a media item.
class SimplePost(Post):
    def __init__(self, postDict):
        super().__init__(postDict)
        self.songURL = postDict[songURLKey]
        self.mediaID = postDict[mediaIDKey]