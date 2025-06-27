import boto3
import json
from ..common import HTTP, Error
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
    postsKey, \
    coverPhotoURLKey, \
    profilePhotoURLKey

# DynamoDB
dynamoDBResourceName = 'dynamodb'
dynamoDBUsersTableName = 'Physical-iOS_Users'
dynamoDBUsernamesTableName = 'Physical-iOS_Usernames'
dynamoDBItemKey = 'Item'
dynamoDBRegionName = 'us-west-1'
dynamodb = boto3.resource(dynamoDBResourceName, region_name=dynamoDBRegionName)
usersTable = dynamodb.Table(dynamoDBUsersTableName)
usernamesTable = dynamodb.Table(dynamoDBUsernamesTableName)

def exchangeUsernameForUserID(username):
    dbResponse = usernamesTable.get_item(
        Key={
            usernameKey: username
        }
    )
    
    item = dbResponse[dynamoDBItemKey]
    return item[userIDKey]

# GET
def getUser(userID):
    # Request the user profile from DynamoDB
    try:
        dbResponse = usersTable.get_item(
            Key={
                userIDKey: userID
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
                postsKey: user.posts,
                coverPhotoURLKey: user.coverPhotoURL,
                profilePhotoURLKey: user.profilePhotoURL
            }
        )
    except: 
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while attempting to add the user to the users table."}))
        
    # Associates user ID and username by adding them to the user ID table in dynamo db.
    try:
        usernamesTable.put_item(
            Item={
                usernameKey: user.username,
                userIDKey: user.userID
            }
        )
    except:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while attempting to associate the specified user ID and username."}))
        
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")

# PUT
def updateUser(userDict):
    # Create a temporary User object
    try:
        user = User(userDict)
    except:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "A required attribute is missing from the request body."}))
        
    # Attempt to update the user's profile
    try:
        usersTable.update_item(
            Key={userIDKey: user.userID},
            UpdateExpression=f"SET {usernameKey} = :{usernameKey}, {displayNameKey} = :{displayNameKey}, {biographyKey} = :{biographyKey}, {coverPhotoURLKey} = :{coverPhotoURLKey}, {profilePhotoURLKey} = :{profilePhotoURLKey}",
            ExpressionAttributeValues={
                f":{usernameKey}": user.username,
                f":{displayNameKey}": user.displayName,
                f":{biographyKey}": user.biography,
                f":{coverPhotoURLKey}": user.coverPhotoURL,
                f":{profilePhotoURLKey}": user.profilePhotoURL
            }
        )
    except:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while attempting to update the user object."}))
    
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")
