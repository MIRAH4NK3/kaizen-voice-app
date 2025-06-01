import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('kaizen_success_story_dresden_dev')

def lambda_handler(event, context):
    try:
        response = table.scan()

        items = response.get('Items', [])
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'stories': items})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
