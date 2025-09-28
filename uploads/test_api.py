#!/usr/bin/env python3
"""
Simple test script for the Image Processing API
"""
import requests
import time
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_upload_image():
    """Test image upload"""
    print("Testing image upload...")
    
    # Create a simple test image
    from PIL import Image
    test_image_path = "test_image.jpg"
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_image_path)
    
    try:
        # Upload the image
        with open(test_image_path, 'rb') as f:
            files = {'file': (test_image_path, f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/newTask", files=files)
        
        print(f"Upload Status: {response.status_code}")
        print(f"Upload Response: {response.json()}")
        
        if response.status_code == 200:
            task_id = response.json()['task_id']
            print(f"Task ID: {task_id}")
            
            # Check task status
            print("Checking task status...")
            for i in range(10):  # Check up to 10 times
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/api/isReady/{task_id}")
                print(f"Status check {i+1}: {status_response.status_code}")
                print(f"Status response: {status_response.json()}")
                
                if status_response.status_code == 200:
                    task_data = status_response.json()
                    if task_data['status'] in ['completed', 'failed']:
                        print(f"Task finished with status: {task_data['status']}")
                        break
            else:
                print("Task did not complete within expected time")
        
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == "__main__":
    print("Starting API tests...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_upload_image()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")
    
    print("=" * 50)
    print("Tests completed!")
