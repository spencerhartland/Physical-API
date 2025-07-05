from ...common import Error
from .Post import Post

# Attribute keys
songURLKey = "songURL"
mediaIDKey = "mediaID"

class SimplePost(Post):
    """
    A simple social post with a caption and content. The post's content may be 
    either a song from Apple Music or an item from the user's collection.
    
    Attributes:
        id: 
            The unique identifier for the post.
        author: 
            The unique identifier for the author of the post.
        timestamp: 
            The date / time that the post was published, represented as seconds since epoch.
        caption: 
            The post's caption.
        songURL: 
            The song's Apple Music URL, if the post contains a song.
        mediaID: 
            The unique identifier of an item in the user's collection, if the post contains a media item.
    """

    def __init__(self, postDict):
        """
        Constructs a new instance of `SimplePost` with data from `postDict`.
        
        Parameters:
            postDict:
                A dictionary containing metadata for a social post of type `SimplePost`.

        Returns:
            The new `SimplePost`.

        Raises:
            KeyError: A required attribute is missing from the post data.
        """

        super().__init__(postDict)
        try:
            self.songURL = postDict[songURLKey]
            self.mediaID = postDict[mediaIDKey]
        except KeyError as error:
            message = "The required attribute " + str(error) + " is missing from post of type `SimplePost`."
            raise KeyError(message)