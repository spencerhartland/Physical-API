import json
from .common import HTTP, Event
from .auth import AuthenticationManager
from .user import UserManager
from .access import AccessManager
import requests

authFunctionPath = "/auth"
tokenFunctionPath = "/auth/token"
userFunctionPath = "/user"
userIDFunctionPath = "/userID"

# Query Params
userIDKey = "userID"
usernameKey = "username"

# Main Lambda handler
def lambda_handler(event, context):
    # Get info about the request from the event
    httpMethod = event.get(Event.httpMethodKey, "")
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
    # /user
    elif path == userFunctionPath:
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

    # Not implemented
    return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
        

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
