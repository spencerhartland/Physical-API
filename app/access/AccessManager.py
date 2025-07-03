import os
import jwt
from cryptography.hazmat.primitives import serialization
from .models.AccessData import AccessData
import time
import secrets
import hashlib
import boto3

privateKeyFile = os.environ['PRIVATE_ACCESS_KEY_FILE']
publicKeyFile = os.environ['PUBLIC_ACCESS_KEY_FILE']

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
    except Exception as error:
        raise error
    
    # Provide access
    return provideAccessFor(sub)

# Checks the validity of an access token.
#
# Parameters:
#   - token: The client's API access token.
def validate(token: str) -> bool:
    publicKey = __retrievePublicKey()
    try:
        _ = jwt.decode(token, key=publicKey, algorithms=["RS256"], audience="com.spencerhartland.Physical", issuer="https://physical.spencerhartland.com")
        return True
    except:
        return False


def __generateAccessTokenFor(sub: str) -> str:
    iat = time.time()
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
    algorithm='RS256'
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

def __retrievePrivateKey() -> serialization.SSHPrivateKeyTypes:
    privateKeyString = open(privateKeyFile, 'r').read()
    return serialization.load_ssh_private_key(privateKeyString.encode(), password=None)

# TODO: Get rid of this - it should be pulled from server?
def __retrievePublicKey() -> serialization.SSHPublicKeyTypes:
    publicKeyString = open(publicKeyFile, 'r').read()
    return serialization.load_ssh_private_key(publicKeyString.encode(), password=None)