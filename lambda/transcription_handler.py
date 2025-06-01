import json
import boto3
import urllib.parse

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
transcribe = boto3.client('transcribe')

BUCKET_NAME = 'kaizen-voice-raw-dresden'
TABLE_NAME = 'kaizen_success_story_dresden_dev'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Scan for all stories in progress
        response = table.scan(
            FilterExpression="transcription_status = :status",
            ExpressionAttributeValues={":status": "IN_PROGRESS"}
        )

        for item in response.get("Items", []):
            story_id = item['story_id']
            timestamp = item['timestamp']  # Required because timestamp is now part of the key
            job_name = f"kaizen-{story_id}"

            try:
                job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                status = job['TranscriptionJob']['TranscriptionJobStatus']

                if status == 'COMPLETED':
                    transcript_obj = json.loads(s3.get_object(
                        Bucket=BUCKET_NAME,
                        Key=f"transcripts/{story_id}.json"
                    )['Body'].read())

                    text = transcript_obj['results']['transcripts'][0]['transcript']

                    table.update_item(
                        Key={'story_id': story_id, 'timestamp': timestamp},
                        UpdateExpression="SET transcription_status = :done, transcript = :t",
                        ExpressionAttributeValues={
                            ':done': 'COMPLETED',
                            ':t': text
                        }
                    )
                    print(f"✅ Story {story_id} updated with transcript.")

                elif status == 'FAILED':
                    table.update_item(
                        Key={'story_id': story_id, 'timestamp': timestamp},
                        UpdateExpression="SET transcription_status = :fail",
                        ExpressionAttributeValues={':fail': 'FAILED'}
                    )
                    print(f"❌ Story {story_id} transcription failed.")

            except Exception as e:
                print(f"Error processing {story_id}: {str(e)}")

        return {
            'statusCode': 200,
            'body': json.dumps('Finished transcription handler run.')
        }

    except Exception as e:
        print("UNHANDLED ERROR:")
        print(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
