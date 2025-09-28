"""
Integration tests for Celery tasks.
"""
import pytest
from unittest.mock import patch, Mock
import tempfile
import os

from app.services.image_processor import ImageProcessor
from app.services.ml_tree_analyzer import MLTreeAnalyzer


class TestProcessImageTask:
    """Test cases for process_image_task Celery task."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_process_image_task_success(self, db_session, sample_image_file):
        """Test successful image processing task."""
        from app.api.routes import process_image_task
        
        # Create test task in database
        from app.models.task import Task
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        # Mock the image processor and ML analyzer
        with patch.object(ImageProcessor, 'validate_image', return_value=True), \
             patch.object(ImageProcessor, 'resize_image', return_value=sample_image_file), \
             patch.object(MLTreeAnalyzer, 'analyze_tree') as mock_analyze:
            
            mock_analyze.return_value = {
                'tree_type': 'oak',
                'confidence': 0.85,
                'health_score': 0.75,
                'damages': []
            }
            
            # Execute the task
            result = process_image_task(task.id)
            
            # Verify task was updated
            db_session.refresh(task)
            assert task.status == "COMPLETED"
            assert task.tree_type == "oak"
            assert task.tree_type_confidence == 0.85
            assert task.overall_health_score == 0.75
    
    @pytest.mark.integration
    def test_process_image_task_invalid_image(self, db_session):
        """Test image processing task with invalid image."""
        from app.api.routes import process_image_task
        
        # Create test task with invalid image path
        from app.models.task import Task
        task = Task(
            original_path="/uploads/original/invalid.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        # Mock file not found
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = process_image_task(task.id)
            
            # Verify task was marked as failed
            db_session.refresh(task)
            assert task.status == "FAILED"
    
    @pytest.mark.integration
    def test_process_image_task_ml_error(self, db_session, sample_image_file):
        """Test image processing task with ML analysis error."""
        from app.api.routes import process_image_task
        
        # Create test task
        from app.models.task import Task
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        # Mock ML analyzer to raise exception
        with patch.object(ImageProcessor, 'validate_image', return_value=True), \
             patch.object(MLTreeAnalyzer, 'analyze_tree', side_effect=Exception("ML Error")):
            
            result = process_image_task(task.id)
            
            # Verify task was marked as failed
            db_session.refresh(task)
            assert task.status == "FAILED"
    
    @pytest.mark.integration
    def test_process_image_task_nonexistent_task(self):
        """Test image processing task with non-existent task ID."""
        from app.api.routes import process_image_task
        
        # Try to process non-existent task
        result = process_image_task(999)
        assert result is None


class TestCeleryTaskIntegration:
    """Test cases for Celery task integration."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_task_lifecycle(self, client, db_session, sample_image_file):
        """Test complete task lifecycle from creation to completion."""
        from app.api.routes import process_image_task
        
        # Create task via API
        files = {"file": ("test.jpg", sample_image_file, "image/jpeg")}
        response = client.post("/api/tasks", files=files)
        assert response.status_code == 201
        
        task_data = response.json()
        task_id = task_data["id"]
        
        # Verify task is in PENDING status
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "PENDING"
        
        # Mock successful processing
        with patch.object(ImageProcessor, 'validate_image', return_value=True), \
             patch.object(ImageProcessor, 'resize_image', return_value=sample_image_file), \
             patch.object(MLTreeAnalyzer, 'analyze_tree') as mock_analyze:
            
            mock_analyze.return_value = {
                'tree_type': 'pine',
                'confidence': 0.92,
                'health_score': 0.88,
                'damages': [{'type': 'disease', 'severity': 0.2}]
            }
            
            # Process the task
            result = process_image_task(task_id)
            
            # Verify task completion
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            
            task_data = response.json()
            assert task_data["status"] == "COMPLETED"
            assert task_data["tree_type"] == "pine"
            assert task_data["tree_type_confidence"] == 0.92
            assert task_data["overall_health_score"] == 0.88
            assert len(task_data["damages_detected"]) == 1
    
    @pytest.mark.integration
    def test_concurrent_task_processing(self, db_session, sample_image_file):
        """Test processing multiple tasks concurrently."""
        from app.api.routes import process_image_task
        import concurrent.futures
        
        # Create multiple tasks
        from app.models.task import Task
        tasks = []
        for i in range(3):
            task = Task(
                original_path=f"/uploads/original/test_{i}.jpg",
                status="PENDING"
            )
            db_session.add(task)
            tasks.append(task)
        db_session.commit()
        
        # Mock successful processing for all tasks
        with patch.object(ImageProcessor, 'validate_image', return_value=True), \
             patch.object(ImageProcessor, 'resize_image', return_value=sample_image_file), \
             patch.object(MLTreeAnalyzer, 'analyze_tree') as mock_analyze:
            
            mock_analyze.return_value = {
                'tree_type': 'oak',
                'confidence': 0.85,
                'health_score': 0.75,
                'damages': []
            }
            
            # Process tasks concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(process_image_task, task.id) for task in tasks]
                results = [future.result() for future in futures]
            
            # Verify all tasks were processed
            for task in tasks:
                db_session.refresh(task)
                assert task.status == "COMPLETED"
