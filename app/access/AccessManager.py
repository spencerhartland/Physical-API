import os
import jwt
from cryptography.hazmat.primitives import serialization
import jwt.algorithms
from .models.AccessData import AccessData
import time
import secrets
import hashlib
import boto3
import requests
import json

privateKeyFile = os.environ['PRIVATE_KEY_FILE']
encryptionPasswordFile = os.environ['ENCRYPTION_PASSWORD_FILE']

# Public key
publicKeyURL = "https://physical.spencerhartland.com/auth/keys"

# DynamoDB
dynamoDBResourceName = 'dynamodb'
dynamoDBTokensTableName = 'Physical-iOS_Tokens'
dynamoDBItemKey = 'Item'
dynamoDBRegionName = 'us-west-1'
dynamodb = boto3.resource(dynamoDBResourceName, region_name=dynamoDBRegionName)
tokensTable = dynamodb.Table(dynamoDBTokensTableName)

def provideAccessFor(sub: str) -> AccessData:
    """
    Generates a new access token and refresh token for the given user.

    Parameters:
        sub: The identifier of the subject (user) to be given access.

    Returns:
        An instance of `AccessData` containing the newly generated tokens.
    """

    accessToken = __generateAccessTokenFor(sub)
    refreshToken = __generateRefreshTokenFor(sub)
    return AccessData(accessToken, refreshToken)

def exchange(token: str) -> AccessData:
    """
    Exchanges a refresh token for a new access token and refresh token.
    
    Parameters:
        token: The client's refresh token.

    Returns:
        An instance of `AccessData` containing the newly generated tokens.
    """

    # Generate the provided token's hash value
    tokenHash = hashlib.sha256(token.encode()).hexdigest()
    # Validate hash
    try:
        # if the hash is in the table, it is valid.
        dbResponse = tokensTable.get_item(
            Key = { "tokenHash": tokenHash }
        )

        # remove the token from the table (one use only)
        _ = tokensTable.delete_item(
            Key = { "tokenHash": tokenHash }
        )

        sub = dbResponse["Item"]["sub"]
    except:
        raise Exception("No record of the provided refresh token.")
    
    # Provide access
    return provideAccessFor(sub)

def validate(token: str) -> dict:
    """
    Checks the validity of an access token.

    Parameters:
        token: The client's API access token.

    Returns:
        The payload of the access token as a dictionary, which contains claims 
        typical of JWT identity tokens. For example:
        ```
        {
            "iss": "https://physical.spencerhartland.com",
            "sub": "user123456",
            "aud": "com.spencerhartland.Physical",
            "iat": 1751651698,
            "exp": 1751655298
        }
        ```
    """

    publicKey = __retrievePublicKeyFor(token)
    return jwt.decode(
        token, 
        key=publicKey, 
        algorithms=["ES256"], 
        audience="com.spencerhartland.Physical", 
        issuer="https://physical.spencerhartland.com"
    )


def __generateAccessTokenFor(sub: str) -> str:
    iat = int(time.time())
    privateKey = __retrievePrivateKey()

    payloadData = {
        "iss": "https://physical.spencerhartland.com",
        "sub": sub,
        "aud": "com.spencerhartland.Physical",
        "iat": iat,
        "exp": iat + 3600
    }

    return jwt.encode(
    payload=payloadData,
    key=privateKey,
    algorithm='ES256'
    )

def __generateRefreshTokenFor(sub: str) -> str:
    # Generate the raw refresh token string
    token = secrets.token_hex(16)
    # Generate the refresh token's hash value
    tokenHash = hashlib.sha256(token.encode()).hexdigest()
    # Store the hash in DB
    try:
        tokensTable.put_item(
            Item={ 
                "tokenHash": tokenHash,
                "sub": sub
            }
        )
    except Exception as error:
        raise error
    
    return token

def __retrievePublicKeyFor(token: str) -> serialization.PublicFormat:
    try:
        header = jwt.get_unverified_header(token)
        keyID = header.get("kid")

        result = requests.get(publicKeyURL)
        jwks = result.json()
        for jwk in jwks["keys"]:
            if keyID == jwk["kid"]:
                return jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(jwk))
    except:
        raise Exception("An error occurred while attempting to fetch the public key.")

def __retrievePrivateKey() -> serialization.PrivateFormat:
    password = __retrieveEncryptionPassword()
    privateKeyBytes = open(privateKeyFile, 'rb').read()
    return serialization.load_pem_private_key(privateKeyBytes, password=password)

def __retrieveEncryptionPassword() -> bytes:
    return open(encryptionPasswordFile, 'rb').read().strip()