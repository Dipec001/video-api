from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from .models import Video
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import WaiterError
import time
from .tasks import start_transcription
from .serializers import VideoSerializer
from rest_framework import generics
from django.http import StreamingHttpResponse
import uuid
import shutil

# Create your views here.
class ListVideosView(generics.ListAPIView):
    """
    View for retrieving a list of all videos.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

# @api_view(['POST'])
# @transaction.atomic
# def upload_video(request):
#     uploaded_video = request.FILES.get('video')

#     if uploaded_video:
#         # Initialize AWS S3 client
#         s3 = boto3.client('s3',
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             region_name=settings.AWS_S3_REGION_NAME
#         )

#         # Define the S3 bucket name
#         bucket_name = settings.AWS_STORAGE_BUCKET_NAME

#         try:
#             # Generate a unique S3 object key (file path)
#             s3_object_key = f'media/{uploaded_video.name}'

#             # Upload the video to the S3 bucket with the generated key
#             s3.upload_fileobj(uploaded_video, bucket_name, s3_object_key)

#             # Create a database record for the uploaded video with the S3 object key
#             video = Video(title='Your Video Title', file_path=s3_object_key)
#             video.save()

#             # Call the transcription function with the S3 URI of the uploaded video
#             input_uri = f's3://{bucket_name}/{s3_object_key}'
#             start_transcription.delay(input_uri)

#             return Response({'message': 'Video uploaded successfully.'}, status=status.HTTP_201_CREATED)
#         except NoCredentialsError:
#             return Response({'message': 'AWS credentials are missing or incorrect.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response({'message': 'Video upload failed.'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def video_playback(request, video_id):
    # Retrieve the video object from the database or return a 404 if it doesn't exist
    video = get_object_or_404(Video, id=video_id)

    # Get the S3 object key (file path) from the video object
    s3_object_key = video.file_path

    try:
        # Initialize AWS S3 client
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Generate a pre-signed URL for the S3 object (video)
        # This URL will be temporary and provide secure access to the video
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_object_key},
            ExpiresIn=3600  # Set expiration time (e.g., 1 hour)
        )

        # Fetch the video content from the pre-signed URL
        response = HttpResponse(status=302)
        response['Location'] = presigned_url

        # Set the Content-Type header to 'video/mp4'
        response['Content-Type'] = 'video/mp4'

        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)
    

@api_view(['GET'])
def get_transcription(request, video_id):
    # Retrieve the video object from the database or return a 404 if it doesn't exist
    video = get_object_or_404(Video, id=video_id)

    # Get the S3 object key (file path) for the transcription
    transcription_key = f'transcripts/{video.file_path.split("/")[-1]}.json'

    # Generate a pre-signed URL for the transcription file
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Generate a pre-signed URL for the S3 object (transcription file)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': transcription_key},
            ExpiresIn=3600  # Set expiration time (e.g., 1 hour)
        )

        return Response({'transcription_url': presigned_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Define a temporary storage directory for video chunks
TEMP_CHUNKS_DIR = os.path.join(settings.MEDIA_ROOT, 'temp_chunks')

@api_view(['POST'])
@transaction.atomic
def upload_video(request):
    uploaded_chunk = request.FILES.get('chunk')
    video_id = request.data.get('video_id')  # Include a video ID to associate chunks
    is_last_chunk = request.data.get('is_last_chunk')

    if uploaded_chunk and video_id:
        try:
            # Determine the file path for this chunk based on the video_id
            chunk_file_path = os.path.join(TEMP_CHUNKS_DIR, video_id, uploaded_chunk.name)

            # Save the received chunk to a temporary location or buffer
            with open(chunk_file_path, 'wb') as destination:
                for chunk in uploaded_chunk.chunks():
                    destination.write(chunk)

            if is_last_chunk == 'true':
                # Concatenate all chunks to create the complete video
                complete_video_path = os.path.join(settings.MEDIA_ROOT, 'complete_videos', f'{uuid.uuid4()}.mp4')

                # Concatenate chunks into the complete video file
                concatenate_chunks(os.path.join(TEMP_CHUNKS_DIR, video_id), complete_video_path)

                # Upload the complete video to AWS S3
                upload_complete_video_to_s3(complete_video_path)

                # Trigger transcription for the complete video
                start_transcription.delay(complete_video_path)

                # Clean up the temporary directory for this video
                shutil.rmtree(os.path.join(TEMP_CHUNKS_DIR, video_id))

                return Response({'message': 'Video uploaded and transcription started.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Chunk uploaded successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({'message': 'Video upload failed.'}, status=status.HTTP_400_BAD_REQUEST)

def concatenate_chunks(temp_dir, complete_video_path):
    # Concatenate all chunks in the temporary directory into the complete video file
    with open(complete_video_path, 'wb') as output_file:
        for chunk_filename in sorted(os.listdir(temp_dir)):
            chunk_path = os.path.join(temp_dir, chunk_filename)
            with open(chunk_path, 'rb') as chunk_file:
                output_file.write(chunk_file.read())

def upload_complete_video_to_s3(video_path):
    try:
        # Initialize AWS S3 client
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Define the S3 bucket name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        # Generate a unique S3 object key (file path)
        s3_object_key = f'media/{os.path.basename(video_path)}'

        # Upload the complete video to the S3 bucket with the generated key
        s3.upload_file(video_path, bucket_name, s3_object_key)

    except NoCredentialsError:
        raise Exception('AWS credentials are missing or incorrect.')