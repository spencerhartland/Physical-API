import json
from .common import HTTP, Event
from .auth import AuthenticationManager
from .user import UserManager
from .access import AccessManager
import requests
from .post import PostManager
from .access.models.AccessToken import AccessToken
import jwt

authFunctionPath = "/auth"
tokenFunctionPath = "/auth/token"
userFunctionPath = "/user"
userIDFunctionPath = "/userID"
postFunctionPath = "/post"

# Query Params
userIDKey = "userID"
usernameKey = "username"

def lambda_handler(event, context):
    """
    Main lambda event handler , the entry-point for the program.

    Parameters:
        event: Dictionary containing the Lambda function event data.
        context: Lambda runtime context.

    Returns:
        Dictionary representation of an HTTP response.
    """

    # Get info about the request from the event
    httpMethod = event.get(Event.httpMethodKey, "")
    headers = event.get(Event.httpHeadersKey)
    path = event.get(Event.pathKey, "")
    queryParams = event.get(Event.queryParamsKey)

    # /auth ANY
    if path == authFunctionPath:
        authData = __getBody(event)
        return authHandler(httpMethod, authData)
    # /auth/token ANY
    elif path == tokenFunctionPath:
        tokenData = __getBody(event)
        return tokenHandler(httpMethod, tokenData)
    else:
        # Validate access token
        try:
            accessTokenString = __getTokenFromAuthorizationHeader(headers)
            accessToken = __verify(accessTokenString)
        except jwt.ExpiredSignatureError:
            return HTTP.response(HTTP.statusUnauthorized, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The access token has expired."}))
        except Exception as error:
            return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":str(error)}))
        
        # /user
        if path == userFunctionPath:
            # GET
            if httpMethod == HTTP.methodGET:
                return fetchUser(queryParams)
            # POST
            elif httpMethod == HTTP.methodPOST:
                userData = __getBody(event)
                return createUser(userData)
            # PUT
            elif httpMethod == HTTP.methodPUT:
                userData = __getBody(event)
                return updateUser(userData)
        # /userID
        elif path == userIDFunctionPath:
            # GET
            if httpMethod == HTTP.methodGET:
                return fetchUserID(queryParams)
            # POST
            elif httpMethod == HTTP.methodPOST:
                return
        # /post
        elif path == postFunctionPath:
            # POST
            if httpMethod == HTTP.methodPOST:
                postData = __getBody(event)
                return publishPost(postData)
            # GET
            elif httpMethod == HTTP.methodGET:
                return fetchPost(queryParams)
            # DELETE
            elif httpMethod == HTTP.methodDELETE:
                return deletePost(queryParams, accessToken.subject)

        # Not implemented
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
        
# API Access
def __getTokenFromAuthorizationHeader(headers: dict) -> str:
    try:
        # Get token from authorization header
        header = headers["Authorization"].split()
        return header[1]
    except:
        raise Exception("The required authorization header is missing or incorrectly formatted.")
    
def __verify(tokenString: str) -> AccessToken:
    try:
        tokenData = AccessManager.validate(tokenString)
        return AccessToken(tokenData)
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidSignatureError:
        raise Exception("The signature of the access token is invalid.")
    except jwt.InvalidIssuerError:
        raise Exception("The issuer of the access token is invalid.")
    except jwt.InvalidAudienceError:
        raise Exception("The audience of the access token is invalid.")
    except:
        raise Exception("There was a problem while validating the provided access token.")

# Function-specific handlers:
# /auth ANY
def authHandler(httpMethod, authData):
    if httpMethod == HTTP.methodPOST:
        return AuthenticationManager.authenticate(authData)
    else:
        # HTTP method is not implemented
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    
# /auth/token ANY
def tokenHandler(httpMethod: str, tokenData: dict) -> requests.Response:
    if httpMethod != HTTP.methodPOST:
        # HTTP method is not implemented
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))

    try:
        token = tokenData["refreshToken"]
        accessData = AccessManager.exchange(token)
        return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(accessData.json()))
    except KeyError:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request body is missing the required attribute: `refreshToken`."}))
    except Exception as error:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":str(error)}))

# /user GET
def fetchUser(queryParams):
    userID = queryParams.get(userIDKey)
    if userID is None or userID == "":
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request is missing the required `userID` parameter."}))
    else:
        return UserManager.getUser(userID)
        
# /user POST
def createUser(userData):
    return UserManager.createUser(userData)
    
# /user PUT
def updateUser(userData):
    return UserManager.updateUser(userData)
    
# /userID GET
def fetchUserID(queryParams):
    username = queryParams.get(usernameKey)
    if username is None or username == "":
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request is missing the required `userID` parameter."}))
    else:
        try:
            userID = UserManager.exchangeUsernameForUserID(username)
            response = { "user ID": userID }
            return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(response))
        except Exception as e:
            return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"There was a problem while attempting to exchange the user ID for username. {e}"}))
            
# /userID POST
def registerUsername(queryParams):
    pass

# /post POST
def publishPost(postData: dict) -> requests.Response:
    try:
        PostManager.publish(postData)
    except Exception as error:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":str(error)}))
    
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")

# /post GET
def fetchPost(queryParams) -> requests.Response:
    try:
        # get post identifier from query parameters
        postID = queryParams.get("postID")
        if postID is None or postID == "":
            raise Exception("Invalid postID.")
        
        # fetch the post
        postData = PostManager.fetch(postID)
    except Exception as error:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":str(error)}))
    
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(postData))

# /post DELETE
def deletePost(queryParams, userID) -> requests.Response:
    try:
        # get post identifier from query parameters
        postID = queryParams.get("postID")
        if postID is None or postID == "":
            raise Exception("Invalid postID.")
        
        # delete the post
        PostManager.delete(postID, userID)
    except:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"Unable to delete post."}))
    
    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, "")

# Extracts http request body from event
def __getBody(event):
    bodyString = event.get(Event.httpBodyKey)
    if not bodyString:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "Request body is empty."}))
        
    try:
        bodyObject = json.loads(bodyString)
    except Exception as e:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"Could not decode the request body. {str(e)}"}))
        
    return bodyObject
