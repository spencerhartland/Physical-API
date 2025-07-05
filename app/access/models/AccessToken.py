# Attribute names / dictionary keys
issuerKey = "iss"
subjectKey = "sub"
audienceKey = "aud"
issuedAtKey = "iat"
expirationKey = "exp"

class AccessToken:
    """
    A JSON Web Token (JWT) that provides information about the authenticated user.

    Attributes:
        issuer:
            The authority that signed and issued this token. Because this API 
            generates the token, this value should be https://physical.spencerhartland.com.
        subject:
            The unique identifier of the user to whom this token was issued.
        audience:
            The recipient of this token. Becuase this token is for Physical iOS, 
            this value should be the client ID of the app: `com.spencerhartland.Physical`.
        issuedAt:
            The time at which the token was issued, in seconds since the Unix epoch.
        expiration:
            The time at which the token expires, in seconds since the Unix epoch.
    """

    def __init__(self, tokenData: dict):
        try:
            self.issuer = tokenData[issuerKey]
            self.subject = tokenData[subjectKey]
            self.audience = tokenData[audienceKey]
            self.issuedAt = tokenData[issuedAtKey]
            self.expiration = tokenData[expirationKey]
        except KeyError as error:
            message = "The required attribute " + str(error) + " is missing from the token data."
            raise Exception(message)
        except:
            raise Exception("An unknown error occurred while attempting to decode the token.")