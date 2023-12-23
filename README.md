
# Physical API

This repository contains the Python code powering the Physical API. `lambda_function.py` is the entry point for the program, as this code is deployed as an AWS Lambda function using a container image. The Physical API and the backend logic is very much a work in progress, so check back for more updates and detailed technical info!

**Note**

Though the code is deployed as a container image, the `Dockerfile` and its contents will not be available on GitHub as it contains sensitive information.

## API Reference

### Endpoints

#### Retrieve user-generated album art

##### URL
> **GET** https://physical.spencerhartland.com/physical-ios/`image ID`.png

##### HTTP Body
None.

##### Response Codes
**200 OK** The request was completed.
***Image*** *content-type: image/png*

#### Upload user-generated album art

##### URL
> **POST** https://physical.spencerhartland.com/physical-ios/`image ID`.png

##### HTTP Body
**Image data** The raw PNG image data.
*content-type: image/png*

##### Response Codes
**200 OK** The request was completed.
*No return value.*

#### Authenticate user

##### URL
> **POST** https://physical.spencerhartland.com/auth
