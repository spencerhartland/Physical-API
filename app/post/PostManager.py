from .models.ListPost import ListPost
from .models.SimplePost import SimplePost
import boto3
from boto3.dynamodb.conditions import Attr

# DynamoDB
dynamoDBResourceName = 'dynamodb'
dynamoDBPostsTableName = 'Physical-iOS_Posts'
dynamoDBUsersTableName = 'Physical-iOS_Users'
dynamoDBItemKey = 'Item'
dynamoDBRegionName = 'us-west-1'
dynamodb = boto3.resource(dynamoDBResourceName, region_name=dynamoDBRegionName)
postsTable = dynamodb.Table(dynamoDBPostsTableName)
usersTable = dynamodb.Table(dynamoDBUsersTableName)

def publish(postData: dict):
    try:
        postType = postData["postType"]
        # verify formatting
        if postType == "SimplePost":
            _ = SimplePost(postData)
        elif postType == "ListPost":
            _ = ListPost(postData)
        # upload post
        postsTable.put_item(Item=postData)
    except KeyError:
        raise Exception("The required attribute 'postType' is missing from the post data.")
    except:
        raise

def fetch(postID: str) -> dict:
    try:
        response = postsTable.get_item(
            Key = { "postID": postID }
        )

        return response[dynamoDBItemKey]
    except:
        raise

def delete(postID: str, userID: str):
    try:
        _ = postsTable.delete_item(
            Key = { "postID": postID },
            ConditionExpression = Attr("author").eq(userID)
        )
    except:
        raise