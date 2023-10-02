# Video Upload API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
   - [List Videos](#list-videos)
   - [Upload a Video](#upload-a-video)
   - [Video Playback](#video-playback)
   - [Get Transcription](#get-transcription)
4. [Sample API Usage](#sample-api-usage)
5. [Known Limitations](#known-limitations)

---

## Introduction

The Video Upload API is designed to facilitate video uploading, playback, and transcription retrieval. It uses Django for the backend and AWS S3 for storing videos and transcriptions. This API is useful for applications that require video management and transcription services.

---

## Prerequisites

Before using the API, ensure you have the following prerequisites installed and set up:

- Python (3.10)
- Django (3.x)
- Django REST framework
- Boto3 (for AWS S3 integration)
- AWS IAM credentials (Access Key ID and Secret Access Key)
- AWS S3 Bucket (for storing videos and transcriptions)

---

## Getting Started

To get started with the Video Upload API, follow these steps:

### List Videos

**Endpoint**: `/api/videos/`

**HTTP Method**: GET

**Description**: Retrieve a list of all videos available in the system.

**Response**: JSON array of video objects with their details, including title and file path.

### Upload a Video

**Endpoint**: `/api/upload/`

**HTTP Method**: POST

**Description**: Upload a video to the system. The video will be stored on AWS S3, and a database record will be created for it.

**Request**: A `multipart/form-data` POST request with the video file.

**Response**: JSON object with a success message upon successful upload.

### Video Playback

**Endpoint**: `/api/playback/{video_id}/`

**HTTP Method**: GET

**Description**: Retrieve a pre-signed URL for secure video playback. The URL will expire after a certain time (e.g., 1 hour).

**Response**: Redirect to the pre-signed URL for video playback.

### Get Transcription

**Endpoint**: `/api/transcription/{video_id}/`

**HTTP Method**: GET

**Description**: Retrieve a pre-signed URL for the transcription file associated with a video. The URL will expire after a certain time (e.g., 1 hour).

**Response**: JSON object with the transcription URL.

---

## Sample API Usage

### List Videos

Retrieve a list of all videos available in the system:

```http
GET /api/videos/
