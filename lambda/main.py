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
    try:
        audio_base64 = event['audio_base64']
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

        table.put_item(Item={
            'id': story_id,
            'timestamp': timestamp,
            's3_key': s3_key,
            'transcription_status': 'IN_PROGRESS'
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Story saved!', 'id': story_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
