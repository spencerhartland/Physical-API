import json
import os
import requests
import base64
import jwt
from ..common import HTTP, Error
from .models.AuthenticationData import AuthenticationData

# Environment variables
clientID = os.environ['CLIENT_ID']
clientSecretFile = os.environ['CLIENT_SECRET_FILE']
validationURL = os.environ['VALIDATION_URL']
publicKeyURL = os.environ['PUBLIC_KEY_URL']
issuer = os.environ['ISSUER']
publicKeyAlgo = os.environ['PUBLIC_KEY_ALGORITHM']

asciiEncoding = "ascii"

# Grant type values
grantTypeAuthorizationCode = "authorization_code"
grantTypeRefreshToken = "refresh_token"

# ID token keys
issuerFieldKey = "iss"
audienceFieldKey = "aud"
expirationFieldKey = "exp"

# Validation request headers
validationHeaders = {
    "Content-Type": "application/x-www-form-urlencoded"
}

def authenticate(authDataDict):
    try:
        authData = AuthenticationData(authDataDict)
    except Error.AttributeNotFoundError:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message": "The authentication data is improperly formmatted."}))
    
    # Get public key from Apple's endpoint
    publicKeys = {}
    publicKeyResponse = requests.get(publicKeyURL)
    if publicKeyResponse.status_code == HTTP.statusOK:
        try:
            jwks = publicKeyResponse.json()
            for jwk in jwks["keys"]:
                keyID = jwk["kid"]
                publicKeys[keyID] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        except:
            return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"Unable to decode response from public keys endpoint."}))
    else:
        return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"Unable to retrieve public key."}))
        
    # Verify identity token using public key
    verified = verifyToken(authData.identityToken, publicKeys)
    if verified:
        validation = validate(authData.authCode, authData.grantType)
        if validation.status_code == HTTP.statusOK:
            return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, validation.text)
        else:
            return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The authorization code could not be validated."}))
    else:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The validity of the identity token could not be verified."}))

def verifyToken(identityToken, keys):
    # Verify key ID in identity token header
    keyID = jwt.get_unverified_header(identityToken)["kid"]
    key = keys[keyID]
    try:
        payload = jwt.decode(identityToken, key=key, algorithms=[publicKeyAlgo], audience=clientID, issuer=issuer)
        return True
    except:
        return False
        
    
def validate(token, grantType):
    clientSecret = __retrieveClientSecret()
    requestData = {
        "client_id": clientID,
        "client_secret": clientSecret,
        "grant_type": grantType
    }
    if grantType == grantTypeAuthorizationCode:
        requestData["code"] = token
    elif grantType == grantTypeRefreshToken:
        requestData["refresh_token"] = token
    
    return requests.post(validationURL, data=requestData, headers=validationHeaders, timeout=10)
        
def __retrieveClientSecret() -> str:
    with open(clientSecretFile, "r") as file:
        return file.read().strip()