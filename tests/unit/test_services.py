"""
Unit tests for service classes.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from app.services.image_processor import ImageProcessor
from app.services.ml_tree_analyzer import MLTreeAnalyzer


class TestImageProcessor:
    """Test cases for ImageProcessor service."""
    
    @pytest.mark.unit
    def test_image_processor_init(self):
        """Test ImageProcessor initialization."""
        processor = ImageProcessor()
        assert processor is not None
    
    @pytest.mark.unit
    def test_validate_image_valid(self, sample_image_file):
        """Test image validation with valid image."""
        processor = ImageProcessor()
        result = processor.validate_image(sample_image_file)
        assert result is True
    
    @pytest.mark.unit
    def test_validate_image_invalid_format(self):
        """Test image validation with invalid format."""
        processor = ImageProcessor()
        invalid_file = io.BytesIO(b"not an image")
        result = processor.validate_image(invalid_file)
        assert result is False
    
    @pytest.mark.unit
    def test_validate_image_too_small(self):
        """Test image validation with too small image."""
        processor = ImageProcessor()
        small_img = Image.new('RGB', (10, 10), color='red')
        small_img_bytes = io.BytesIO()
        small_img.save(small_img_bytes, format='JPEG')
        small_img_bytes.seek(0)
        
        result = processor.validate_image(small_img_bytes)
        assert result is False
    
    @pytest.mark.unit
    def test_validate_image_too_large(self):
        """Test image validation with too large image."""
        processor = ImageProcessor()
        large_img = Image.new('RGB', (10000, 10000), color='red')
        large_img_bytes = io.BytesIO()
        large_img.save(large_img_bytes, format='JPEG')
        large_img_bytes.seek(0)
        
        result = processor.validate_image(large_img_bytes)
        assert result is False
    
    @pytest.mark.unit
    def test_resize_image(self, sample_image_file):
        """Test image resizing functionality."""
        processor = ImageProcessor()
        resized = processor.resize_image(sample_image_file, max_size=(500, 500))
        
        assert resized is not None
        img = Image.open(resized)
        assert img.width <= 500
        assert img.height <= 500
    
    @pytest.mark.unit
    def test_save_image(self, temp_upload_dir, sample_image_file):
        """Test image saving functionality."""
        processor = ImageProcessor()
        file_path = f"{temp_upload_dir}/test_image.jpg"
        
        result = processor.save_image(sample_image_file, file_path)
        assert result is True
        
        import os
        assert os.path.exists(file_path)


class TestMLTreeAnalyzer:
    """Test cases for MLTreeAnalyzer service."""
    
    @pytest.mark.unit
    def test_ml_analyzer_init(self):
        """Test MLTreeAnalyzer initialization."""
        analyzer = MLTreeAnalyzer()
        assert analyzer is not None
    
    @pytest.mark.unit
    @patch('app.services.ml_tree_analyzer.torch')
    @patch('app.services.ml_tree_analyzer.cv2')
    def test_analyze_tree_mock(self, mock_cv2, mock_torch, sample_image_file):
        """Test tree analysis with mocked ML models."""
        # Mock the ML model and predictions
        mock_model = Mock()
        mock_model.return_value = {
            'tree_type': 'oak',
            'confidence': 0.85,
            'health_score': 0.75,
            'damages': []
        }
        
        analyzer = MLTreeAnalyzer()
        analyzer.model = mock_model
        
        result = analyzer.analyze_tree(sample_image_file)
        
        assert result is not None
        assert 'tree_type' in result
        assert 'confidence' in result
        assert 'health_score' in result
        assert 'damages' in result
    
    @pytest.mark.unit
    def test_analyze_tree_no_model(self, sample_image_file):
        """Test tree analysis without ML model (fallback mode)."""
        analyzer = MLTreeAnalyzer()
        analyzer.model = None  # Simulate no model loaded
        
        result = analyzer.analyze_tree(sample_image_file)
        
        # Should return default/fallback values
        assert result is not None
        assert 'tree_type' in result
        assert 'confidence' in result
        assert 'health_score' in result
        assert 'damages' in result
    
    @pytest.mark.unit
    def test_preprocess_image(self, sample_image_file):
        """Test image preprocessing for ML analysis."""
        analyzer = MLTreeAnalyzer()
        processed = analyzer.preprocess_image(sample_image_file)
        
        assert processed is not None
        # Should return processed image data suitable for ML model
    
    @pytest.mark.unit
    def test_postprocess_results(self):
        """Test postprocessing of ML analysis results."""
        analyzer = MLTreeAnalyzer()
        
        raw_results = {
            'tree_type': 'oak',
            'confidence': 0.85,
            'health_score': 0.75,
            'damages': [{'type': 'disease', 'severity': 0.3}]
        }
        
        processed = analyzer.postprocess_results(raw_results)
        
        assert processed is not None
        assert processed['tree_type'] == 'oak'
        assert processed['tree_type_confidence'] == 0.85
        assert processed['overall_health_score'] == 0.75
        assert len(processed['damages_detected']) == 1
