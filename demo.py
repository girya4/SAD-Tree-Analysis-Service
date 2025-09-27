#!/usr/bin/env python3
"""
Demo script for Image Processing Service
"""
import requests
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api"

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image
        img = Image.new('RGB', (400, 300), color='red')
        img.save('demo_image.jpg')
        print("✓ Created test image: demo_image.jpg")
        return True
    except ImportError:
        print("✗ PIL not available, using existing test image")
        if os.path.exists('test_image.jpg'):
            return True
        return False

def demo_api():
    """Demonstrate the API functionality"""
    print("🚀 Image Processing Service Demo")
    print("=" * 50)
    
    # Create test image
    if not create_test_image():
        print("❌ No test image available")
        return
    
    # Use existing test image if demo image creation failed
    image_file = 'demo_image.jpg' if os.path.exists('demo_image.jpg') else 'test_image.jpg'
    
    session = requests.Session()
    
    try:
        # 1. Get session
        print("\n1. Getting user session...")
        response = session.get(f"{API_BASE}/get-session")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Session created: User ID {data['user_id']}")
        else:
            print(f"✗ Failed to get session: {response.status_code}")
            return
        
        # 2. Upload image
        print("\n2. Uploading image...")
        with open(image_file, 'rb') as f:
            files = {'file': (image_file, f, 'image/jpeg')}
            response = session.post(f"{API_BASE}/newTask", files=files)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data['task_id']
            print(f"✓ Image uploaded successfully! Task ID: {task_id}")
        else:
            print(f"✗ Upload failed: {response.status_code}")
            return
        
        # 3. Check status
        print("\n3. Checking processing status...")
        max_attempts = 10
        for attempt in range(max_attempts):
            response = session.get(f"{API_BASE}/isReady/{task_id}")
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                print(f"   Attempt {attempt + 1}: Status = {status}")
                
                if status == 'completed':
                    print("✓ Image processing completed!")
                    
                    # Show metadata
                    if data.get('task_metadata'):
                        import json
                        metadata = json.loads(data['task_metadata'])
                        print(f"\n📊 Processing Results:")
                        print(f"   Original size: {metadata['original_size']} bytes")
                        print(f"   Processed size: {metadata['processed_size']} bytes")
                        print(f"   Original dimensions: {metadata['original_dimensions'][0]}x{metadata['original_dimensions'][1]}")
                        print(f"   Processed dimensions: {metadata['processed_dimensions'][0]}x{metadata['processed_dimensions'][1]}")
                        compression = (1 - metadata['processed_size'] / metadata['original_size']) * 100
                        print(f"   Compression ratio: {compression:.1f}%")
                    
                    break
                elif status == 'failed':
                    print("✗ Image processing failed!")
                    break
                else:
                    time.sleep(2)
            else:
                print(f"✗ Status check failed: {response.status_code}")
                break
        else:
            print("✗ Processing timeout")
        
        # 4. Health check
        print("\n4. Checking service health...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service is healthy: {data['message']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
        
        print("\n🎉 Demo completed successfully!")
        print(f"\n🌐 Access the web interface at: {BASE_URL}/frontend/")
        print(f"📚 API documentation at: {BASE_URL}/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the service is running:")
        print("   docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_api()
