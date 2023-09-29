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

# Create your views here.
    
@api_view(['POST'])
@transaction.atomic
def upload_video(request):
    uploaded_video = request.FILES.get('video')

    if uploaded_video:
        # Initialize AWS S3 client
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Define the S3 bucket name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            # Generate a unique S3 object key (file path)
            s3_object_key = f'media/{uploaded_video.name}'

            # Upload the video to the S3 bucket with the generated key
            s3.upload_fileobj(uploaded_video, bucket_name, s3_object_key)

            # Create a database record for the uploaded video with the S3 object key
            video = Video(title='Your Video Title', file_path=s3_object_key)
            video.save()

            return Response({'message': 'Video uploaded successfully.'}, status=status.HTTP_201_CREATED)
        except NoCredentialsError:
            return Response({'message': 'AWS credentials are missing or incorrect.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'message': 'Video upload failed.'}, status=status.HTTP_400_BAD_REQUEST)




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