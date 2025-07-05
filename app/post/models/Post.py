from ...common import Error

# Attribute keys
postTypeKey = "postType"
postIDKey = "postID"
authorKey = "author"
timestampKey = "timestamp"
captionKey = "caption"

class Post:
    """
    The abstract superclass for all posts.
    
    Attributes:
        id: 
            The unique identifier for the post.
        author: 
            The unique identifier for the author of the post.
        timestamp: 
            The date / time that the post was published, represented as seconds since epoch.
        caption: 
            The post's caption.
    """
    
    def __init__(self, postDict):
        """
        Constructs a new instance of `Post` with data from `postDict`. Do not 
        call this method directly - instead, initialize a post of type 
        `SimplePost` or `ListPost`.
        
        Parameters:
            postDict:
                A dictionary containing metadata common to all social posts.

        Returns:
            The new `Post`.

        Raises:
            KeyError: A required attribute is missing from the post data.
        """
        
        try:
            self.postType = postDict[postTypeKey]
            self.id = postDict[postIDKey]
            self.author = postDict[authorKey]
            self.timestamp = postDict[timestampKey]
            self.caption = postDict[captionKey]
        except KeyError as error:
            message = "The required attribute " + str(error) + " is missing from the post."
            raise KeyError(message)