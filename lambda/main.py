import json
import boto3
import base64
import uuid
from datetime import datetime

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('kaizen_success_story_dresden_dev')

BUCKET_NAME = 'kaizen-voice-raw-dresden'

def lambda_handler(event, context):
    print("RAW EVENT:")
    print(json.dumps(event))

    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        audio_base64 = body['audio_base64']
        audio_bytes = base64.b64decode(audio_base64)
        story_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        s3_key = f"audio/{story_id}.webm"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=audio_bytes,
            ContentType='audio/webm'
        )

        media_uri = f"s3://{BUCKET_NAME}/{s3_key}"

        transcribe.start_transcription_job(
            TranscriptionJobName=f"kaizen-{story_id}",
            Media={'MediaFileUri': media_uri},
            MediaFormat='webm',
            LanguageCode='en-US',
            OutputBucketName=BUCKET_NAME,
            OutputKey=f"transcripts/{story_id}.json"
        )

        print("📥 Attempting to write to DynamoDB...")
        table.put_item(Item={
            'story_id': story_id,
            'timestamp': timestamp,
            's3_key': s3_key,
            'transcription_status': 'IN_PROGRESS',
            'category': 'Uncategorized',
            'name': 'Unknown',
            'shift': 'Unassigned'
        })
        print("✅ Successfully wrote to DynamoDB.")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Story saved!', 'id': story_id})
        }

    except Exception as e:
        print("ERROR:")
        print(str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
