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
# Check `grantType` to determine whether to use authorization code or refresh token.
class AuthenticationData:
    def __init__(self, authDataDict):
        
        # First, check the grant type
        try:
            grantType = authDataDict[grantTypeKey]
        except:
            raise Error.AttributeNotFoundError(grantTypeKey)
            
        self.grantType = grantType
        
        if grantType == grantTypeAuthorizationCode:
            # Get the authorization code
            try:
                authCode = authDataDict[authCodeKey]
            except:
                raise Error.AttributeNotFoundError(authCodeKey)
                
            self.authCode = authCode
        elif grantType == grantTypeRefreshToken:
            # Get the refresh token
            try:
                refreshToken = authDataDict[refreshTokenKey]
            except:
                raise Error.AttributeNotFoundError(refreshTokenKey)
                
            self.refreshToken = refreshToken
                
        # Get the identity token (JWT)
        try:
            identityToken = authDataDict[identityTokenKey]
        except:
            raise Error.AttributeNotFoundError(identityTokenKey)
            
        self.identityToken = identityToken
