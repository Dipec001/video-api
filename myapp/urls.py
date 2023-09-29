from django.urls import path
from . import views

urlpatterns = [
    # Define the URL pattern for video upload
    path('api/upload', views.upload_video, name='upload_video'),
    path('video/play/<int:video_id>/', views.video_playback, name='video_playback'),

    # Define the URL pattern for retrieving video metadata
    # path('api/videos/', views.get_videos, name='get_videos'),
]