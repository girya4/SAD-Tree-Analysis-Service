#!/usr/bin/env python3
"""
Demo script for Tree Analysis Service v2.0
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
        img = Image.new('RGB', (400, 300), color='green')
        img.save('demo_tree.jpg')
        print("✓ Created test tree image: demo_tree.jpg")
        return True
    except ImportError:
        print("✗ PIL not available, using existing test image")
        if os.path.exists('test_image.jpg'):
            return True
        return False

def demo_ml_tree_analysis():
    """Demonstrate the ML tree analysis functionality"""
    print("🌳 Tree Analysis Service v2.0 Demo")
    print("=" * 50)
    
    # Create test image
    if not create_test_image():
        print("❌ No test image available")
        return
    
    # Use existing test image if demo image creation failed
    image_file = 'demo_tree.jpg' if os.path.exists('demo_tree.jpg') else 'test_image.jpg'
    
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
        
        # 2. Upload multiple images
        print("\n2. Uploading multiple tree images...")
        files = []
        for i in range(3):  # Upload 3 copies
            files.append(('files', (f'tree_{i}.jpg', open(image_file, 'rb'), 'image/jpeg')))
        
        response = session.post(f"{API_BASE}/newTasks", files=files)
        
        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        if response.status_code == 200:
            data = response.json()
            task_ids = data['task_ids']
            print(f"✓ Successfully uploaded {len(task_ids)} images!")
            print(f"  Task IDs: {task_ids}")
        else:
            print(f"✗ Upload failed: {response.status_code}")
            return
        
        # 3. Monitor tasks
        print("\n3. Monitoring ML analysis progress...")
        completed_tasks = []
        max_attempts = 20
        
        for attempt in range(max_attempts):
            print(f"\n   Attempt {attempt + 1}:")
            
            for task_id in task_ids:
                if task_id in completed_tasks:
                    continue
                    
                response = session.get(f"{API_BASE}/isReady/{task_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data['status']
                    print(f"     Task {task_id}: {status}")
                    
                    if status == 'completed':
                        completed_tasks.append(task_id)
                        print(f"     ✓ Task {task_id} completed!")
                        
                        # Show ML results
                        if data.get('tree_type'):
                            print(f"       🌳 Tree Type: {data['tree_type'].title()}")
                            print(f"       📊 Confidence: {data['tree_type_confidence']*100:.1f}%")
                            print(f"       💚 Health Score: {data['overall_health_score']:.3f}")
                            
                            if data.get('damages_detected'):
                                import json
                                damages = json.loads(data['damages_detected'])
                                if damages:
                                    print(f"       ⚠️  Detected Issues:")
                                    for damage in damages:
                                        print(f"         - {damage['type'].replace('_', ' ').title()}")
                                        print(f"           Severity: {damage['severity']}")
                                        print(f"           Confidence: {damage['confidence']*100:.1f}%")
                                        print(f"           Description: {damage['description']}")
                                else:
                                    print(f"       ✅ No issues detected")
                            else:
                                print(f"       ✅ No issues detected")
                    
                    elif status == 'failed':
                        print(f"     ✗ Task {task_id} failed!")
                        completed_tasks.append(task_id)
            
            if len(completed_tasks) == len(task_ids):
                break
                
            time.sleep(3)
        
        # 4. Show task list
        print("\n4. Getting complete task list...")
        response = session.get(f"{API_BASE}/tasks?per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['total']} total tasks")
            
            for task in data['tasks'][:3]:  # Show first 3
                print(f"  Task {task['id']}: {task['status']}")
                if task.get('tree_type'):
                    print(f"    Tree: {task['tree_type']} ({task['tree_type_confidence']*100:.1f}%)")
                    print(f"    Health: {task['overall_health_score']:.3f}")
        
        # 5. Health check
        print("\n5. Checking service health...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service is healthy: {data['message']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
        
        print("\n🎉 Demo completed successfully!")
        print(f"\n🌐 Access the web interface at: {BASE_URL}/frontend/")
        print(f"📚 API documentation at: {BASE_URL}/docs")
        print(f"🔍 Celery monitoring at: {BASE_URL}/flower/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the service is running:")
        print("   docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_ml_tree_analysis()
