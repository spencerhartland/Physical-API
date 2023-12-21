import boto3
import json
from ..common import HTTP, Error
from .models.UserID import UserID

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
        
        userProfileString = dbResponse[dynamoDBItemKey]
    except:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"A problem ocurred while requesting the user profile."}))
    
    try:
        userProfile = json.loads(userProfileString)
    except Exception as e:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"User does not have a profile."}))
        
    # Return the user profile
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(userProfile))
"""
 # POST
def createUser(userObject):
    # The unique user identifier assigned to the user by Apple.
    userID = userObject.get(, "")
    # The unique username chosen by the user.
    username = userObject.get(, "")
    # The user's chosen display name.
    displayName = userObject.get(, "")
    # The user's biography.
    biography = userObject.get(, "")
    # The unique user identifiers of the user's followers.
    followers = userObject.get(, "")
    # The unique user identifiers of the user's followed accounts.
    following = userObject.get(, "")
    # The Music Item ID of the user's featured Music Item.
    featured = userObject.get(, "")
    # The unique identifier of the user's collection.
    collection = userObject.get(, "")
    # The unique identifiers of the user's authored posts.
    posts = userObject.get(, "")
"""
