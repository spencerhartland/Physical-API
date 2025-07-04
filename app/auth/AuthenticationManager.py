import json
import os
import requests
import base64
import jwt
from ..common import HTTP, Error
from .models.AuthenticationData import AuthenticationData
from ..access import AccessManager

# Environment variables
clientSecretFile = os.environ['CLIENT_SECRET_FILE']

clientID = "com.spencerhartland.Physical"
validationURL = "https://appleid.apple.com/auth/token"
publicKeyURL = "https://appleid.apple.com/auth/keys"
issuer = "https://appleid.apple.com"
publicKeyAlgo = "RS256"
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

# Authenticates a user based on the provided authentication data from 
# Sign in with Apple.
#
# Parameters:
#   - authDataDict: A dictionary with specific formatting that contains 
#       information required to authenticate a user. See `AuthenticationData.py`.
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
        
    try:
        # Verify identity token using Apple's public key
        identityToken = verifyToken(authData.identityToken, publicKeys)
        # Validate authorization code with Apple ID server
        validation = validate(authData.authCode, authData.grantType)
        if validation.status_code == HTTP.statusOK:
            try:
                # Get Sign in with Apple (SIWA) refresh token
                tokenResponse = validation.json()
            except:
                return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"TokenResponse object could not be decoded."}))
            
            SIWARefreshToken = tokenResponse["refresh_token"]
            # Get user ID from identity token
            sub = identityToken["sub"]
            
            try:
                # Generate API access token and refresh token for user
                accessData = AccessManager.provideAccessFor(sub)
            except Exception as error:
                print(error)
                return HTTP.response(HTTP.statusInternalError, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"Unable to store token hash."}))
            
            authResponse = {
                "SIWARefreshToken": SIWARefreshToken,
                "accessToken": accessData.accessToken,
                "refreshToken": accessData.refreshToken
            }
            return HTTP.response(HTTP.statusOK, HTTP.standardHTTPResponseHeaders, json.dumps(authResponse))
        else:
            return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The authorization code could not be validated."}))
    except:
        return HTTP.response(HTTP.statusBadRequest, HTTP.standardHTTPResponseHeaders, json.dumps({"message":"The authenticity of the identity token could not be confirmed."}))

# Verifies the signature and claims of a JSON Web Token obtained by a user 
# authenticating via Sign in with Apple.
#
# Parameters:
#   - identityToken: The Apple-provided JWT to be verified.
#   - keys: A list of public keys which contains the key needed to verify 
#       the token. This is provided by the issuer of the token (Apple).
def verifyToken(identityToken, keys) -> dict:
    # Get public key ID from JWT header
    keyID = jwt.get_unverified_header(identityToken)["kid"]
    # Get key from list of Apple's public keys
    key = keys[keyID]
    try:
        # `decode` handles verification of signature and claims. If not verfied, it will raise an error.
        return jwt.decode(identityToken, key=key, algorithms=[publicKeyAlgo], audience=clientID, issuer=issuer)
    except Exception as error:
        raise error
        

# Validates the provided token with Apple using the client secret. Refresh 
# tokens may be validated a maximum of once per day, further requests will 
# be throttled.
#
# Parameters:
#   - token: Either an authorization code (first time) or refresh token.
#   - grantType: A string indicating the type of token being validated.
def validate(token, grantType) -> requests.Response:
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