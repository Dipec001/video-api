from django.urls import path
from . import views

urlpatterns = [
    # Define the URL pattern for video upload
    path('api/upload_video/', views.upload_video, name='upload_video'),
    path('api/video/play/<int:video_id>/', views.video_playback, name='video_playback'),
    path('api/videos/', views.ListVideosView.as_view(), name='list_videos'),
    path('api/get_transcription/<int:video_id>/', views.get_transcription, name='get_transcription'),
    # path('start_transcription/', views.start_transcription, name='start_transcription'),

    # Define the URL pattern for retrieving video metadata
    # path('api/videos/', views.get_videos, name='get_videos'),
]
