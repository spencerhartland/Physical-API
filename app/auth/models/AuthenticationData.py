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
        grantType = authDataDict[grantTypeKey]
        if not grantType:
            raise Error.AttributeNotFoundError(grantTypeKey)
            
        self.grantType = grantType
        
        if grantType == grantTypeAuthorizationCode:
            # Get the authorization code
            authCode = authDataDict[authCodeKey]
            if not authCode:
                raise Error.AttributeNotFoundError(authCodeKey)
                
            self.authCode = authCode
        elif grantType == grantTypeRefreshToken:
            # Get the refresh token
            refreshToken = authDataDict[refreshTokenKey]
            if not refreshToken:
                raise Error.AttributeNotFoundError(refreshTokenKey)
                
            self.refreshToken = refreshToken
                
        # Get the identity token (JWT)
        identityToken = authDataDict[identityTokenKey]
        if not identityToken:
            raise Error.AttributeNotFoundError(identityTokenKey)
            
        self.identityToken = identityToken
