import boto3
import json
from ..common import HTTP, Error
from .models.UserID import UserID
from .models.User import User
from .models.User import \
    userIDKey, \
    usernameKey, \
    displayNameKey, \
    biographyKey, \
    followersKey, \
    followingKey, \
    featuredKey, \
    collectionKey, \
    postsKey

# DynamoDB
dynamoDBResourceName = 'dynamodb'
dynamoDBUsersTableName = 'Physical-iOS-users'
dynamoDBItemKey = 'Item'
dynamoDBRegionName = 'us-west-1'
dynamodb = boto3.resource(dynamoDBResourceName, region_name=dynamoDBRegionName)
usersTable = dynamodb.Table(dynamoDBUsersTableName)

# GET
# userIDDict should be formatted like so:
#   { "userID": "<user ID>" }
def getUser(userIDDict):
    try:
        userID = UserID(userIDDict)
    except Error.AttributeNotFoundError:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "Request body is missing the user ID."}))
    
    # Request the user profile from DynamoDB
    try:
        dbResponse = usersTable.get_item(
            Key={
                userIDKey: userID.rawValue
            }
        )
        
        userProfile = dbResponse[dynamoDBItemKey]
    except Exception as e:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"A problem ocurred while attempting to retrieve the user profile. {e}"}))
        
    # Return the user profile
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(userProfile))
    
# POST
def createUser(userDict):
    
    # Create the user object
    # Doing so ensures that all required attributes are present.
    try:
        user = User(userDict)
    except:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "A required attribute is missing from the request body."}))
    
    # Create the user in the users table
    try:
        usersTable.put_item(
            Item={
                userIDKey: user.userID,
                usernameKey: user.username,
                displayNameKey: user.displayName,
                biographyKey: user.biography,
                followersKey: user.followers,
                followingKey: user.following,
                featuredKey: user.featured,
                collectionKey: user.collection,
                postsKey: user.posts
            }
        )
    except:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while attempting to add the user to the users table."}))
        
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")
