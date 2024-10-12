import math
import boto3
from decimal import Decimal
import json

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

def lambda_handler(event, context):
    if 'timestamp' in event:
        temp = float(event['temp'])
        sensor_table = dynamodb.Table('dht22_2_table_andres')
        response = sensor_table.put_item(
            Item={
                'app_id': "sensor",
                'timestamp': int(event['timestamp']),
                'temp': str(event['temp']),
                'hum': str(event['hum'])
            }
        )

        print(response)
        if temp > 25:
            send_email(temp)

        ws_table = dynamodb.Table('ws_connection_id_andres')

        response = ws_table.scan()
        connection_items = response.get('Items', [])
        
        api_client = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url='https://re4xscfbzl.execute-api.us-east-1.amazonaws.com/production/'
        )
        
        for item in connection_items:
            connection_id = item.get('connectionId')
            if connection_id:
                try:
                    api_client.post_to_connection(
                        ConnectionId=connection_id,
                        Data=json.dumps({'temp': event['temp'], 'hum': event['hum'], 'timestamp': event['timestamp']})
                    )
                    print(f"Message sent to connectionId: {connection_id}")
                except Exception as e:
                    print(f"Error sending message to connectionId {connection_id}: {e}")
        
        # Return
        return "DB updated"

def send_email(temp):
    sender_email = "iot.meng.2.2024@gmail.com"
    recipient_email = "ajbustos@uniquindio.edu.co"
    subject = "Temperature Alert: High Temperature Detected"
    body = f"Warning! The current temperature has exceeded 25°C. Current temperature: {temp}°C."
    
    response = ses.send_email(
        Source=sender_email,
        Destination={
            'ToAddresses': [
                recipient_email,
            ]
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    
    print(f"Email sent! Message ID: {response['MessageId']}")
