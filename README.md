# Video API Documentation

Welcome to the Video API documentation. This API allows you to upload screenrecorded videos, view, and transcribe videos. It also provides access to video playback and transcription URLs.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [List Videos](#list-videos)
  - [Video Playback](#video-playback)
  - [Get Transcription](#get-transcription)
  - [Upload Video](#upload-video)
- [Sample Requests and Responses](#sample-requests-and-responses)

## Prerequisites

Before using this API, ensure you have the following prerequisites in place:

- Python 3.x
- Django (version 3.x)
- AWS S3 Bucket (for video storage)
- AWS Access Key ID and Secret Access Key
- Boto3 (Python SDK for AWS)
- Django Rest Framework

## Getting Started

### Installation

Clone this repository:

```bash
   git clone <repository-url>
   cd videoproject
---

Install the required dependencies:
```
 pip install -r requirements.txt
Configuration
Configure your Django settings to use AWS S3 for media storage. Update the following settings in your settings.py:
```
   AWS_ACCESS_KEY_ID = 'your-access-key-id'
   AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'
   AWS_STORAGE_BUCKET_NAME = 'your-s3-bucket-name'
   AWS_S3_REGION_NAME = 'your-s3-region-name'
   MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```


## API ENDPOINTS

### List Videos

**Endpoint**: `https://video-api-85ac12263247.herokuapp.com/api/videos/`

**HTTP Method**: GET

**Description**: Retrieve a list of all videos available in the system.

**Response**: JSON array of video objects with their details, including title and file path.

### Upload Video

**Endpoint**: `https://video-api-85ac12263247.herokuapp.com/api/upload-video/`

**HTTP Method**: POST

**Description**: Video received in chunks into the system for later assembly into a complete video. Chunks are associated with a video by providing a video ID. The last chunk will trigger video concatenation, S3 upload, transcription, and cleanup so the is_last_chunk param should be set to `True`.

**Request**: A `multipart/form-data` POST request with the video chunk file, video ID, and an indicator for the last chunk.

**Response**: JSON object with a success message upon successful chunk upload or video upload.


### Video Playback

**Endpoint**: `https://video-api-85ac12263247.herokuapp.com/api/video/play/{video_id}/`

**HTTP Method**: GET

**Description**: Retrieve the video playback URL for a specific video and other video details.

**Response**: JSON object with details

### Get Transcription

**Endpoint**: `https://video-api-85ac12263247.herokuapp.com/api/get_transcription/{video_id}/`

**HTTP Method**: GET

**Description**: Retrieve a pre-signed URL for the transcription file associated with a video.

**Response**: JSON object with the transcription URL.

---

## Sample API Usage

### List Videos

Retrieve a list of all videos available in the system:

```http
GET https://video-api-85ac12263247.herokuapp.com/api/videos/
```

Sample Response:
```
[
  {
    "id": 1,
    "title": "Sample Video 1",
    "file_path": "media/sample_video_1.mp4"
  },
  {
    "id": 2,
    "title": "Sample Video 2",
    "file_path": "media/sample_video_2.mp4"
  }
]

```
Upload Video

Upload video chunks to the system:

```http
POST https://video-api-85ac12263247.herokuapp.com/api/upload_video/
```

Sample Response:
```
{
  "message": "Video uploaded and transcription started."
}
```

Video Playback

Retrieve a pre-signed URL for secure video playback:

```http
GET https://video-api-85ac12263247.herokuapp.com/api/video/play/1/
```
Sammple Response:
```
{
    "upload_id": 1,
    "created_on": "2023-10-01T12:34:56Z",
    "filename": "Video Title",
    "url": "https://your-s3-bucket.s3.amazonaws.com/media/video_12345.mp4",
    "transcript_url": "/api/get_transcription/1/"
}

```
Get Transcription
```Request
GET https://video-api-85ac12263247.herokuapp.com/api/get_transcription/1/

```
Response (Transcript Available)
```
{
    "transcription_url": "https://your-s3-bucket.s3.amazonaws.com/transcripts/video_12345.mp4.json"
}

```
Response (Transcript Not Available)
```
{
    "message": "No transcript available for this video."
}

```
The Api Link
```
https://video-api-85ac12263247.herokuapp.com/
```

Known Limitations

This API does not include authentication or authorization mechanisms. It assumes open access.
Error handling for invalid requests is minimal in this sample.
