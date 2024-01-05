import boto3
import json
from ..common import HTTP, Error
from .models.UserRequest import \
    idTypeUsername, \
    idTypeUserID, \
    UserRequest
from .models.User import User
from .models.User import \
    usernameKey, \
    userIDKey, \
    displayNameKey, \
    biographyKey, \
    followersKey, \
    followingKey, \
    featuredKey, \
    collectionKey, \
    postsKey

# DynamoDB
dynamoDBResourceName = 'dynamodb'
dynamoDBUsersTableName = 'Physical-iOS_Users'
dynamoDBUserIDsTableName = 'Physical-iOS_User-IDs'
dynamoDBItemKey = 'Item'
dynamoDBRegionName = 'us-west-1'
dynamodb = boto3.resource(dynamoDBResourceName, region_name=dynamoDBRegionName)
usersTable = dynamodb.Table(dynamoDBUsersTableName)
userIDsTable = dynamodb.Table(dynamoDBUserIDsTableName)

def exchangeUserIDForUsername(userID):
    dbResponse = userIDsTable.get_item(
        Key={
            userIDKey: userID
        }
    )
    
    item = dbResponse[dynamoDBItemKey]
    return item[usernameKey]

# GET
def getUser(idType, identifier):
    try:
        userRequest = UserRequest(idType, identifier)
    except Exception as e:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": f"{e}"}))
    
    # Set correct search key
    if userRequest.idType == idTypeUsername:
        idType = usernameKey
    elif userRequest.idType == idTypeUserID:
        idType = userIDKey
    
    # Request the user profile from DynamoDB
    try:
        dbResponse = usersTable.get_item(
            Key={
                idType: userRequest.identifier
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
                usernameKey: user.username,
                userIDKey: user.userID,
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
        
    # Add user ID to User IDs table.
    try:
        userIDsTable.put_item(
            Item={
                userIDKey: user.userID,
                usernameKey: user.username
            }
        )
    except:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while attempting to add the user ID to the User IDs table."}))
        
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")
