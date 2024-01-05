import json
from .common import HTTP, Event
from .auth import AuthenticationManager
from .user import UserManager

authFunctionName = "auth"
userFunctionName = "user"
usernameFunctionName = "username"

# Query Params
idTypeKey = "idType"
identifierKey = "identifier"
userIDKey = "userID"

def lambda_handler(event, context):
    # Get the HTTP method
    httpMethod = event.get(Event.httpMethodKey, "")
    queryParams = event.get(Event.queryParamsKey)
    
    if context.function_name == authFunctionName:
        if httpMethod == HTTP.methodPOST:
            authDict = getBody(event)
            return AuthenticationManager.authenticate(authDict)
        else:
            # HTTP method is not POST
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    elif context.function_name == userFunctionName:
        if httpMethod == HTTP.methodGET:
            idType = queryParams.get(idTypeKey)
            identifier = queryParams.get(identifierKey)
            if idType is None or idType == "":
                return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request is missing the required `idType` parameter."}))
            elif identifier is None or identifier == "":
                return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request is missing the required `identifier` parameter."}))
            else:
                return UserManager.getUser(idType, identifier)
        elif httpMethod == HTTP.methodPOST:
            userDict = getBody(event)
            return UserManager.createUser(userDict)
        else:
            # HTTP method is not implemented
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    elif context.function_name ==  usernameFunctionName:
        if httpMethod == HTTP.methodGET:
            userID = queryParams.get(userIDKey)
            if userID is None or userID == "":
                return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The request is missing the required `userID` parameter."}))
            else:
                try:
                    username = UserManager.exchangeUserIDForUsername(userID)
                    response = { "username": username }
                    return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(response))
                except Exception as e:
                    return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"There was a problem while attempting to exchange the user ID for username. {e}"}))
        else:
            # HTTP method is not implemented
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))

# Extracts http request body from event
def getBody(event):
    bodyString = event.get(Event.httpBodyKey, "")
    if not bodyString:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "Request body is empty."}))
        
    try:
        bodyObject = json.loads(bodyString)
    except Exception as e:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":f"Could not decode the request body. {str(e)}"}))
        
    return bodyObject
