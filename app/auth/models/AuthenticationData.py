from ...common import Error

# Dictionary keys
grantTypeKey = "grantType"
authCodeKey = "authorizationCode"
refreshTokenKey = "refreshToken"
identityTokenKey = "identityToken"

# Grant type values
grantTypeAuthorizationCode = "authorization_code"
grantTypeRefreshToken = "refresh_token"


# An object containing an authorization code or refresh token along with a JSON web token.
#
# Attributes:
#    - grantType: The grant type for the authentication request. Either "authorization_code" or "refresh_token."
#    - authCode: If the grant type is authorization code, this attribute contains an authorization code obtained from Sign In With Apple.
#    - refreshToken: If the grant type is refresh token, this attribute contains a refresh token obtained from the Sign In With Apple API.
#    - identityToken: A JSON Web Token (JWT) containing information that can be used to identify the user authenticating.
class AuthenticationData:
    def __init__(self, authDataDict):
        
        # First, check the grant type
        try:
            self.grantType = authDataDict[grantTypeKey]
        except:
            raise Error.AttributeNotFoundError(grantTypeKey)
        
        if self.grantType == grantTypeAuthorizationCode:
            # Get the authorization code
            try:
                self.authCode = authDataDict[authCodeKey]
            except:
                raise Error.AttributeNotFoundError(authCodeKey)
        elif self.grantType == grantTypeRefreshToken:
            # Get the refresh token
            try:
                self.refreshToken = authDataDict[refreshTokenKey]
            except:
                raise Error.AttributeNotFoundError(refreshTokenKey)
                
        # Get the identity token (JWT)
        try:
            self.identityToken = authDataDict[identityTokenKey]
        except:
            raise Error.AttributeNotFoundError(identityTokenKey)
