import boto3
from botocore.exceptions import WaiterError
from django.conf import settings
import time
from rest_framework.response import Response
from celery import shared_task

# Initialize the Transcribe client
transcribe = boto3.client('transcribe', region_name=settings.AWS_S3_REGION_NAME)

def start_transcription(input_uri, timeout_seconds=300, polling_interval=5):
    try:
        job_name = f'TranscriptionJob_{int(time.time())}'

        # Extract the input video file name from the input_uri
        input_video_name = input_uri.split('/')[-1]

        # Use the input video name as the base name for the output key
        output_key = f'transcripts/{input_video_name}.json'

        # Start transcription job
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': input_uri},
            MediaFormat='mp4',
            LanguageCode='en-US',  # Change the language code as needed
            OutputBucketName=settings.AWS_STORAGE_BUCKET_NAME,
            OutputKey=output_key,  # Adjust the output key as needed
        )

        # Poll for job completion or failure with a timeout
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_seconds:
                return Response({'message': 'Transcription job timeout'}, status=500)

            status = transcribe.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']

            if job_status in ['COMPLETED', 'FAILED']:
                break  # Exit the loop when the job is completed or has failed

            time.sleep(polling_interval)

        # Once the job is completed, you can fetch the results
        if job_status == 'COMPLETED':
            transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return Response({'message': 'Transcription completed successfully', 'transcript_url': transcript_url}, status=200)
        else:
            # Handle the case when the job has failed
            error_message = status.get('TranscriptionJob').get('FailureReason', 'Transcription job failed')
            return Response({'message': error_message}, status=500)

    except WaiterError as e:
        # Handle any WaiterError exceptions if needed
        return Response({'message': f'Error: {str(e)}'}, status=500)