import json
import boto3
import uuid
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ws_connection_id_andres')

    if event['requestContext']['routeKey'] == '$connect':
        connectionId = event['requestContext']['connectionId']
        userId = str(uuid.uuid4())

        table.put_item(
            Item={
                'app_id': userId,
                'connectionId': connectionId
            }
        )

    if event['requestContext']['routeKey'] == '$disconnect':
        connectionId = event['requestContext']['connectionId']

        response = table.scan(
            FilterExpression=Attr('connectionId').eq(connectionId)
        )
        
        if 'Items' in response and response['Items']:
            userId = response['Items'][0]['app_id']
            table.delete_item(
                Key={'app_id': userId}
            )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
