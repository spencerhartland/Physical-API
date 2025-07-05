from ...common import Error
from .Post import Post

# Attribute keys
listKey = "list"

class ListPost(Post):
    """
    A social post with a caption and an ordered list of songs from Apple Music.
    
    Attributes:
        id:
            The unique identifier for the post.
        author:
            The unique identifier for the author of the post.
        timestamp:
            The date / time that the post was published, represented as seconds since epoch.
        caption:
            The post's caption.
        list:
            An ordered list containing URLs to songs on Apple Music.
    """
    
    def __init__(self, postDict):
        """
        Constructs a new instance of `ListPost` with data from `postDict`.
        
        Parameters:
            postDict:
                A dictionary containing metadata for a social post of type `ListPost`.

        Returns:
            The new `ListPost`.

        Raises:
            KeyError: A required attribute is missing from the post data.
        """
        
        super().__init__(postDict)
        try:
            self.list = postDict[listKey]
        except KeyError as error:
            message = "The required attribute " + str(error) + " is missing from post of type `ListPost`."
            raise KeyError(message)