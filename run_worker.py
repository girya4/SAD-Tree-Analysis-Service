#!/usr/bin/env python3
"""
Script to run Celery worker locally for development
"""
import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import celery
        import redis
        import sqlalchemy
        import pillow
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main function"""
    print("Image Processing Service - Celery Worker")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\nStarting Celery worker...")
    print("Make sure Redis is running on localhost:6379")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start Celery worker
    try:
        subprocess.run([
            "celery", "-A", "celery_app", "worker", 
            "--loglevel=info", "--concurrency=2"
        ])
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
    except FileNotFoundError:
        print("Error: Celery not found. Make sure it's installed: pip install celery")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
