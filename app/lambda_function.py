import json
from .common import HTTP, Event
from .auth import AuthenticationManager
from .user import UserManager

authFunctionName = "auth"
userFunctionName = "user"

def lambda_handler(event, context):
    # Get the HTTP method
    httpMethod = event.get(Event.httpMethodKey, "")
    #if context.function_name == authFunctionName:
    if httpMethod == HTTP.methodPOST:
        authObject = getBody(event)
        return AuthenticationManager.authenticate(authObject)
    else:
        # HTTP method is not POST
        return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    """
    elif context.function_name == userFunctionName:
        if httpMethod == HTTP.methodGET:
            userIDObject = getBody(event)
            return UserManager.getUser(userIDObject)
        else:
            # HTTP method is not GET
            return HTTP.response(HTTP.statusNotImplemented, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The requested method has not been implemented."}))
    """

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
