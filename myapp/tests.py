from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import os

class VideoUploadTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_chunks_dir = 'C:/Users/Dpecc/OneDrive/Documents/temp_chunks'  # Update with your actual path

    def test_upload_video(self):
        # Define the video_id, is_last_chunk, and chunk data for testing
        video_id = '12345'
        is_last_chunk = 'true'
        
        # Create a temporary chunk file for testing
        chunk_file_content = b'Test chunk data'
        chunk_file = SimpleUploadedFile("test_chunk.webm", chunk_file_content, content_type="video/mp4")
        
        chunk_data = {
            'video_id': video_id,
            'is_last_chunk': is_last_chunk,
            'chunk': chunk_file  # Attach the chunk file to the request data
        }

        # Simulate uploading a chunk
        response = self.client.post('/api/upload_video/', data=chunk_data, format='multipart', HTTP_CONTENT_TYPE='video/mp4')

        # Assert that the response status code is as expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Add more assertions based on your expected behavior

        # Clean up the temporary chunk file (if necessary)
        chunk_file.close()
        os.remove(chunk_file.temporary_file_path())

