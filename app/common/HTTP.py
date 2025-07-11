# Standard response headers
standardHTTPResponseHeaders = {
    "Content-Type": "application/json"
}

statusOK = 200
statusBadRequest = 400
statusUnauthorized = 401
statusInternalError = 500
statusNotImplemented = 501

# HTTP methods
methodGET = "GET"
methodPOST = "POST"
methodPUT = "PUT"
methodDELETE = "DELETE"

# Creates a properly formatted response object for AWS to turn into an HTTP response
def response(statusCode, headers, body):
    return {
        "statusCode": statusCode,
        "headers": headers,
        "body": body
    }
