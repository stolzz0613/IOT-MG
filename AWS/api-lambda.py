import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('dht22_2_table_andres')

    if 'requestContext' in event and 'routeKey' in event['requestContext']:
        route_key = event['requestContext']['routeKey']
        connection_id = event['requestContext']['connectionId']
        
        if route_key == '$connect':
            user_id = event.get('queryStringParameters', {}).get('userId', 'unknown_user')
            table.put_item(
                Item={
                    'app_id': user_id,
                    'connectionId': connection_id
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps('Connected successfully')
            }

        elif route_key == '$disconnect':
            response = table.scan(
                FilterExpression=Key('connectionId').eq(connection_id)
            )
            if 'Items' in response and response['Items']:
                user_id = response['Items'][0]['app_id']
                table.delete_item(
                    Key={'app_id': user_id}
                )
            return {
                'statusCode': 200,
                'body': json.dumps('Disconnected successfully')
            }

    if 'resource' in event and event['resource'] == '/data':
        query_params = event.get('queryStringParameters', {})
        if query_params and 'start_timestamp' in query_params and 'end_timestamp' in query_params:
            start_timestamp = query_params['start_timestamp']
            end_timestamp = query_params['end_timestamp']
            response = table.query(
                KeyConditionExpression=Key('app_id').eq('sensor') & Key('timestamp').between(int(start_timestamp), int(end_timestamp))
            )
            body = response['Items']
        else:
            body = table.scan()['Items']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(body, cls=JSONEncoder)
        }

    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Bad Request: Missing or invalid resource'})
    }
