from ...common import Error
import Post

# Attribute keys
listKey = "list"

# A social post with a caption and an ordered list of songs from Apple Music.
#
# Attributes:
#    - id: The unique identifier for the post.
#    - author: The unique identifier for the author of the post.
#    - timestamp: The date / time that the post was published, represented as seconds since epoch.
#    - caption: The post's caption.
#    - list: An ordered list containing URLs to songs on Apple Music.
class ListPost(Post):
    def __init__(self, postDict):
        super().__init__(postDict)
        self.list = postDict[listKey]