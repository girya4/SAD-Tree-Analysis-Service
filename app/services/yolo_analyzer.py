"""
YOLO-based Tree Analysis Service
Integrates YOLO v11 models for tree detection and defect analysis
"""
import uuid
from pathlib import Path
import cv2
import numpy as np
import torch
import ultralytics
from ultralytics import YOLO
import os
import sys
import json
import tempfile
from typing import Dict, List, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Defect translations
DEFECT_TRANSLATIONS = {
    "crack": "трещина",
    # Add more translations as needed
}

class YOLOTreeAnalyzer:
    """
    YOLO-based tree analyzer for detection and defect analysis
    """
    
    def __init__(self, models_dir: str = "app/ml_models"):
        """
        Initialize YOLO models

        Args:
            models_dir: Directory containing model files
        """
        self.models_dir = Path(models_dir)
        self.seg_model_path = self.models_dir / 'yolo11l-seg_tree_detection.pt'
        self.defect_model_path = self.models_dir / 'yolo11l-seg_tree_defects.pt'

        # Force CPU usage
        self.device = 'cpu'
        
        # Initialize models
        try:
            logger.info("Loading YOLO models for CPU inference...")
            logger.info(f"Segmentation model path: {self.seg_model_path}")
            logger.info(f"Defect model path: {self.defect_model_path}")
            
            # Check if model files exist
            if not self.seg_model_path.exists():
                raise FileNotFoundError(f"Segmentation model not found: {self.seg_model_path}")
            if not self.defect_model_path.exists():
                raise FileNotFoundError(f"Defect model not found: {self.defect_model_path}")
            
            # Load models with explicit device setting
            self.seg_model = YOLO(str(self.seg_model_path))
            self.defect_model = YOLO(str(self.defect_model_path))
            
            logger.info(f"YOLO models loaded successfully on device: {self.device}")
        except Exception as e:
            logger.error(f"Failed to load YOLO models: {e}")
            raise
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze image for trees and defects
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            return self._process_photo(image_path)
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            raise
    
    def _process_photo(self, img_path: str) -> Dict:
        """
        Process photo using YOLO models

        Args:
            img_path: Path to the image

        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Processing image: {img_path}")
            seg_res = self.seg_model(img_path, device=self.device)
        except Exception as e:
            logger.error(f"Error in segmentation model: {e}")
            raise RuntimeError(f"Segmentation failed: {e}")
        photo_dict = {}

        for photo in seg_res:
            photo_id = str(uuid.uuid4())
            n_segments = len(photo)
            img = np.copy(photo.orig_img)
            photo_dict["id_фото"] = photo_id
            photo_dict["n"] = n_segments
            photo_dict["trees"] = []

            for ci, c in enumerate(photo):
                tree_dict = {}
                label = c.names[c.boxes.cls.tolist().pop()]
                conf = round(float(c.boxes.conf[0]), 2)
                x, y, w, h = c.boxes.xywh.cpu().numpy().astype(int).tolist()[0]
                tree_id = f"tree_{ci + 1}"
                
                # Convert to format expected by React frontend
                tree_dict["id_tree"] = tree_id
                tree_dict["вид"] = self._translate_species(label)
                tree_dict["достоверность_предсказания"] = conf
                tree_dict["x_координата_начала_рамки"] = max(0, x - w//2)
                tree_dict["y_координата_начала_рамки"] = max(0, y - h//2)
                tree_dict["ширина_рамки"] = w
                tree_dict["высота_рамки"] = h

                # Process defects
                defects = self._analyze_defects(img, c, tree_id)
                tree_dict["повреждения"] = defects

                photo_dict["trees"].append(tree_dict)
                
        return photo_dict
    
    def _analyze_defects(self, img: np.ndarray, contour_data, tree_id: str) -> List[str]:
        """
        Analyze defects for a specific tree contour
        
        Args:
            img: Original image
            contour_data: YOLO contour detection data
            tree_id: Unique tree identifier
            
        Returns:
            List of detected defects in Russian
        """
        defects = []
        
        try:
            # Create mask for isolated tree
            b_mask = np.zeros(img.shape[:2], np.uint8)
            contour = contour_data.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
            _ = cv2.drawContours(b_mask, [contour], -1, (255, 255, 255), cv2.FILLED)
            isolated = np.dstack([img, b_mask])
            
            # Create temporary file for defect analysis
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                cv2.imwrite(tmp_file.name, isolated)
                
                # Analyze defects
                defections = self.defect_model(tmp_file.name, device=self.device)[0].cpu()
                defect_labels = [
                    str(defections.names[cls.item()])
                    for cls in defections.boxes.cls.int()
                ]
                
                # Translate defects to Russian
                defects = [self._translate_defect(defect) for defect in defect_labels]
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
        except Exception as e:
            logger.warning(f"Error analyzing defects for tree {tree_id}: {e}")
            
        return defects
    
    def _translate_species(self, species: str) -> str:
        """
        Translate species name to scientific/Russian name
        
        Args:
            species: English species name
            
        Returns:
            Translated species name
        """
        species_mapping = {
            "tree": "Дерево (неопределенный вид)",
            "oak": "Quercus robur",
            "pine": "Pinus sylvestris",
            "birch": "Betula pendula",
            "maple": "Acer platanoides",
            # Add more mappings as needed
        }
        
        return species_mapping.get(species.lower(), species)
    
    def _translate_defect(self, defect: str) -> str:
        """
        Translate defect name to Russian
        
        Args:
            defect: English defect name
            
        Returns:
            Russian defect name
        """
        defect_mapping = {
            "crack": "трещина",
            "hole": "дупло", 
            "bark_damage": "повреждение коры",
            "dead_branch": "сухая ветка",
            "insect_damage": "повреждение насекомыми",
            # Add more mappings as needed
        }
        
        return defect_mapping.get(defect.lower(), defect)


# Global analyzer instance (singleton pattern)
_analyzer_instance: Optional[YOLOTreeAnalyzer] = None

def get_yolo_analyzer() -> YOLOTreeAnalyzer:
    """
    Get singleton instance of YOLO analyzer
    
    Returns:
        YOLOTreeAnalyzer instance
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = YOLOTreeAnalyzer()
    return _analyzer_instance


def analyze_tree_image_yolo(image_path: str) -> Dict:
    """
    Convenience function for tree analysis using YOLO
    
    Args:
        image_path: Path to the tree image
        
    Returns:
        Dict with analysis results in React frontend format
    """
    analyzer = get_yolo_analyzer()
    return analyzer.analyze_image(image_path)


# CLI interface (for backward compatibility)
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="YOLO v11 computer vision model for \
                                     segmentation trees and bushes and detecting plant defects")
    parser.add_argument("img_path", help="The path to the input file.")
    args = parser.parse_args()
    
    try:
        photo_dict = analyze_tree_image_yolo(args.img_path)
        json_string = json.dumps(photo_dict, ensure_ascii=False, indent=2)
        sys.stdout.write(json_string)
    except Exception as e:
        error_dict = {"error": str(e)}
        json_string = json.dumps(error_dict)
        sys.stdout.write(json_string)
        sys.exit(1)