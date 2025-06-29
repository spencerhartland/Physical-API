
# Physical API

This repository contains the Python code powering the Physical API. `lambda_function.py` is the entry point for the program, as this code is deployed as an AWS Lambda function using a container image. The Physical API and the backend logic is very much a work in progress, so check back for more updates and detailed technical info!

## API Reference

### Fetch user-generated album art

#### URL
> **GET** `https://physical.spencerhartland.com/physical-ios/<image ID>.png`

#### HTTP Body
None.

#### Response Codes
**200 OK** The request was completed.  
***Image*** *Content-Type: image/png*

### Upload user-generated album art

#### URL
> **POST** `https://physical.spencerhartland.com/physical-ios/<image ID>.png`

#### HTTP Body
**Image data** The raw PNG image data.  
*Content-Type: image/png*

#### Response Codes
**200 OK** The request was completed.  
*No return value.*

### Authenticate user

#### URL
> **POST** `https://physical.spencerhartland.com/auth`

##### HTTP Body
**JSON Object** The authentication request body, which contains information required to authenticate the user.  
*Content-Type: application/json*

##### Properties

**grantType**: *String* The grant type used by the authentication request. Either `authorization_code` or `refresh_token`.

**authorizationCode**: *String* If the grant type is `authorization_code`, the authorization code obtained from Sign In With Apple.

**refreshToken**: *String* If the grant type is `refresh_token`, the refresh token obtained from the Sign In With Apple API.

**identityToken**: *String* A JSON Web Token (JWT) containing information that can be used to identify the user.

#### Response Codes
**200 OK** The user was authenticated.  
*No return value.*

**400 Bad Request** The server was unable to process the request.  
***ErrorResponse*** *Content-Type: application/json*

**500 Internal Error** The server encountered an internal error while processing the request.  
***ErrorResponse*** *Content-Type: application/json*

### Fetch user account

#### URL
> **GET** `https://physical.spencerhartland.com/user`

### Create user account

#### URL
> **POST** `https://physical.spencerhartland.com/user`
