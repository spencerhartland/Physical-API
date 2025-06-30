import json
from .common import HTTP, Event
from .auth import AuthenticationManager
from .user import UserManager

authFunctionPath = "/auth"
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
    
    if path == authFunctionPath:
        authData = getBody(event)
        return authHandler(httpMethod, authData)
    elif path == userFunctionPath:
        if httpMethod == HTTP.methodGET:
            return fetchUser(queryParams)
        elif httpMethod == HTTP.methodPOST:
            userData = getBody(event)
            return createUser(userData)
        elif httpMethod == HTTP.methodPUT:
            userData = getBody(event)
            return updateUser(userData)
        else:
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    elif path == userIDFunctionPath:
        if httpMethod == HTTP.methodGET:
            return fetchUserID(queryParams)
        elif httpMethod == HTTP.methodPOST:
            return
        else:
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    else:
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))

# Function-specific handlers

# /auth ANY
def authHandler(httpMethod, authData):
    if httpMethod == HTTP.methodPOST:
        return AuthenticationManager.authenticate(authData)
    else:
        # HTTP method is not implemented
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
        
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
def getBody(event):
    bodyString = event.get(Event.httpBodyKey)
    if not bodyString:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "Request body is empty."}))
        
    try:
        bodyObject = json.loads(bodyString)
    except Exception as e:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"Could not decode the request body. {str(e)}"}))
        
    return bodyObject
