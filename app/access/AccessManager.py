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

# Generates an access token and a refresh token for the user.
#
# Parameters:
#   - sub: The identifier of the subject (user) to be given access.
def provideAccessFor(sub: str) -> AccessData:
    accessToken = __generateAccessTokenFor(sub)
    refreshToken = __generateRefreshTokenFor(sub)
    return AccessData(accessToken, refreshToken)

# Exchanges a refresh token for a new access token and refresh token.
#
# Parameters:
#   - token: The client's refresh token.
def exchange(token: str) -> AccessData:
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
        raise Exception("No record of the provided refresh token. Obtain a new token by authenticating with your Apple Account.")
    
    # Provide access
    return provideAccessFor(sub)

# Checks the validity of an access token.
#
# Parameters:
#   - token: The client's API access token.
def validate(token: str) -> bool:
    publicKey = __retrievePublicKeyFor(token)
    try:
        _ = jwt.decode(token, key=publicKey, algorithms=["ES256"], audience="com.spencerhartland.Physical", issuer="https://physical.spencerhartland.com")
        return True
    except:
        return False


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
    header = jwt.get_unverified_header(token)
    keyID = header.get("kid")

    result = requests.get(publicKeyURL)
    jwks = result.json()
    for jwk in jwks["keys"]:
        if keyID == jwk["kid"]:
            return jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(jwk))

def __retrievePrivateKey() -> serialization.PrivateFormat:
    password = __retrieveEncryptionPassword()
    privateKeyBytes = open(privateKeyFile, 'rb').read()
    return serialization.load_pem_private_key(privateKeyBytes, password=password)

def __retrieveEncryptionPassword() -> bytes:
    return open(encryptionPasswordFile, 'rb').read().strip()