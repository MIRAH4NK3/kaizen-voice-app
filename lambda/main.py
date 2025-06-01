import json
import boto3
import uuid
from datetime import datetime
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    body = json.loads(event['body'])

    story_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    item = {
        "story_id": story_id,
        "timestamp": timestamp,
        "associate_name": body.get("associate_name", "anonymous"),
        "category": body.get("category", "general"),
        "summary": body.get("summary", "No summary provided."),
    }

    table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Story saved!', 'id': story_id})
    }
