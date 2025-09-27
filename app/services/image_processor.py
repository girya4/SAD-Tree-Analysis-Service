import os
import json
from pathlib import Path
from PIL import Image
from celery import current_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.task import Task, TaskStatus, TreeType
from app.utils.file_utils import create_processed_dir
from app.services.ml_tree_analyzer import analyze_tree_image
from celery_app import celery_app


@celery_app.task(bind=True)
def process_image(self, task_id: int):
    """Process uploaded image with ML tree analysis"""
    db = SessionLocal()
    
    try:
        # Get task from database
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        # Update status to processing
        task.status = TaskStatus.PROCESSING
        db.commit()
        
        # Process the image
        original_path = Path(task.original_path)
        if not original_path.exists():
            raise Exception(f"Original file not found: {original_path}")
        
        # Create processed directory
        processed_dir = create_processed_dir()
        
        # Generate processed filename
        processed_filename = f"processed_{original_path.name}"
        processed_path = processed_dir / processed_filename
        
        # Open and process image
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize image (example: resize to max 800x600 while maintaining aspect ratio)
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            # Save processed image
            img.save(processed_path, 'JPEG', quality=85)
        
        # Perform ML tree analysis
        print(f"Starting ML analysis for task {task_id}...")
        ml_results = analyze_tree_image(str(original_path))
        print(f"ML analysis completed for task {task_id}")
        
        # Update task with result
        task.result_path = str(processed_path)
        task.status = TaskStatus.COMPLETED
        
        # Store ML analysis results
        task.tree_type = TreeType(ml_results['tree_type'])
        task.tree_type_confidence = ml_results['tree_type_confidence']
        task.damages_detected = json.dumps(ml_results['damages_detected'])
        task.overall_health_score = ml_results['overall_health_score']
        
        # Add legacy metadata for backward compatibility
        metadata = {
            "original_size": os.path.getsize(original_path),
            "processed_size": os.path.getsize(processed_path),
            "original_dimensions": Image.open(original_path).size,
            "processed_dimensions": Image.open(processed_path).size,
            "ml_analysis": ml_results
        }
        task.task_metadata = json.dumps(metadata)
        
        db.commit()
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result_path": str(processed_path),
            "ml_results": ml_results,
            "metadata": metadata
        }
        
    except Exception as e:
        # Update task status to failed
        if 'task' in locals():
            task.status = TaskStatus.FAILED
            task.task_metadata = json.dumps({"error": str(e)})
            db.commit()
        
        # Re-raise the exception for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()
