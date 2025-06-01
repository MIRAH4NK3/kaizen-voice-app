import json
import boto3
import urllib.parse

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
transcribe = boto3.client('transcribe')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')

BUCKET_NAME = 'kaizen-voice-raw-dresden'
TABLE_NAME = 'kaizen_success_story_dresden_dev'
table = dynamodb.Table(TABLE_NAME)

def analyze_transcript(text):
    prompt = f"""
You are a Lean and Six Sigma operations analyst helping categorize employee voice reports from a delivery station.

Analyze the following transcript and extract:
1. Category — choose from:
   - Standard Work
   - 5S / Workplace Organization
   - Error Proofing / Poka-Yoke
   - Andon / Escalation
   - Safety & Ergonomics
   - General Kaizen
   - Flow Efficiency / Bottlenecks
   - Takt Time & Staffing Balance
   - Defect Detection / Quality at Source
   - Visual Management
   - Training & Cross-Skilling
   - Voice of Associate (VoA)
   - Customer Obsession
2. Name of the associate (first name if possible)
3. Shift or department (e.g. Night Shift, Early Shift, HR, ORM, Drivers)

Return the result in this JSON format:
{{
  "category": "Example Category",
  "name": "FirstName",
  "shift": "Night Shift"
}}

Transcript:
{text}
"""
response = bedrock_runtime.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.2
    })
)
 
    response_body = json.loads(response['body'].read())
    result = json.loads(response_body['content'][0]['text'])
    return result  # includes category, name, shift

def lambda_handler(event, context):
    try:
        # Scan for all stories in progress
        response = table.scan(
            FilterExpression="transcription_status = :status",
            ExpressionAttributeValues={":status": "IN_PROGRESS"}
        )

        for item in response.get("Items", []):
            story_id = item['story_id']
            timestamp = item['timestamp']
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
                    result = analyze_transcript(text)

                    table.update_item(
                        Key={'story_id': story_id, 'timestamp': timestamp},
                        UpdateExpression="""
                            SET transcription_status = :done,
                                transcript = :t,
                                category = :c,
                                name = :n,
                                shift = :s
                        """,
                        ExpressionAttributeValues={
                            ':done': 'COMPLETED',
                            ':t': text,
                            ':c': result['category'],
                            ':n': result['name'],
                            ':s': result['shift']
                        }
                    )
                    print(f"✅ Story {story_id} updated with category '{result['category']}', name '{result['name']}', shift '{result['shift']}'.")

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
