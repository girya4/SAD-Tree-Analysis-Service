"""
ML Tree Analysis Service - Real YOLO Implementation
Uses YOLO models for tree analysis
"""
import random
import time
import json
import os
from typing import Dict, List, Tuple, Optional
from app.models.task import TreeType, DamageType
from app.config.ml_config import ml_config

# Import YOLO analyzer
try:
    from app.services.yolo_analyzer import analyze_tree_image_yolo
    YOLO_AVAILABLE = True
    print("YOLO analyzer loaded successfully")
except ImportError as e:
    print(f"YOLO analyzer not available: {e}")
    YOLO_AVAILABLE = False


class MLTreeAnalyzer:
    """
    Real YOLO ML service for tree analysis
    Uses YOLO models for actual tree detection and analysis
    """
    
    def __init__(self):
        self.config = ml_config
        # Always use real ML - YOLO only
        self.use_real_ml = YOLO_AVAILABLE
        
        if self.use_real_ml:
            print("Using real YOLO ML models for analysis")
        else:
            print("ERROR: YOLO models not available!")
            raise RuntimeError("YOLO models are required but not available")
    
    def analyze_tree(self, image_path: str, additional_params: Dict = None) -> Dict:
        """
        Analyze tree image using YOLO models

        Args:
            image_path: Path to the tree image
            additional_params: Additional parameters for analysis

        Returns:
            Dict with YOLO analysis results
        """
        start_time = time.time()
        
        # Use real YOLO analysis
        try:
            results = self._analyze_with_yolo(image_path)
        except Exception as e:
            print(f"YOLO analysis failed: {e}")
            raise RuntimeError(f"YOLO analysis failed: {e}")
        
        # Add processing metadata
        processing_time = time.time() - start_time
        results['processing_time'] = round(processing_time, 2)
        results['image_path'] = image_path
        results['additional_params'] = additional_params or {}
        results['ml_model_version'] = "YOLO11"
        results['analysis_method'] = "YOLO"
        
        return results
    
    def _analyze_with_yolo(self, image_path: str) -> Dict:
        """
        Analyze image using real YOLO models
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dict with YOLO analysis results converted to legacy format
        """
        # Get YOLO results in React format
        yolo_results = analyze_tree_image_yolo(image_path)
        
        # Convert to legacy format for backward compatibility
        if yolo_results.get("trees"):
            first_tree = yolo_results["trees"][0]  # Use first detected tree
            
            # Map species to TreeType enum
            species_mapping = {
                "Quercus robur": TreeType.OAK,
                "Pinus sylvestris": TreeType.PINE,
                "Betula pendula": TreeType.BIRCH,
                "Acer platanoides": TreeType.MAPLE,
            }
            
            tree_type = TreeType.UNKNOWN
            for species, tree_enum in species_mapping.items():
                if species in first_tree.get("вид", ""):
                    tree_type = tree_enum
                    break
            
            # Convert defects to legacy format
            damages = []
            for defect in first_tree.get("повреждения", []):
                damage_info = {
                    'type': 'bark_damage',  # Default type
                    'confidence': 0.8,
                    'severity': 'medium',
                    'description': defect,
                    'recommendations': ["Обратиться к специалисту"]
                }
                damages.append(damage_info)
            
            # Calculate health score based on defects
            health_score = max(0.3, 1.0 - len(damages) * 0.2)
            
            return {
                'tree_type': tree_type.value,
                'tree_type_confidence': first_tree.get("достоверность_предсказания", 0.8),
                'damages_detected': damages,
                'overall_health_score': health_score,
                'analysis_timestamp': time.time(),
                'yolo_raw_data': yolo_results  # Keep original YOLO data
            }
        else:
            # No trees detected, return default
            return {
                'tree_type': TreeType.UNKNOWN.value,
                'tree_type_confidence': 0.0,
                'damages_detected': [],
                'overall_health_score': 0.5,
                'analysis_timestamp': time.time(),
                'yolo_raw_data': yolo_results
            }
    
    def analyze_for_react_frontend(self, image_path: str) -> Dict:
        """
        Analyze image and return results in React frontend format
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dict with results in React frontend format
        """
        try:
            # Use real YOLO analysis directly
            return analyze_tree_image_yolo(image_path)
        except Exception as e:
            print(f"YOLO analysis failed: {e}")
            raise RuntimeError(f"YOLO analysis failed: {e}")
    
    def _generate_mock_results(self) -> Dict:
        """
        Generate realistic mock analysis results
        
        ML OUTPUT CONFIGURATION:
        ========================
        
        To add new output fields:
        1. Add new fields to the return dictionary below
        2. Update database model in app/models/task.py (optional - new fields are nullable)
        3. Update API schemas in app/api/schemas.py
        4. Update frontend rendering in frontend/index.html
        
        To modify existing fields:
        1. Update the field generation logic below
        2. Update frontend display logic if needed
        
        Note: Database changes are optional - new fields are nullable by default
        """
        
        # Determine tree type based on probabilities
        tree_type = self._select_tree_type()
        tree_confidence = random.uniform(*self.config.TREE_CONFIDENCE_RANGE)
        
        # Generate damage analysis
        damages = self._generate_damage_analysis()
        
        # Calculate overall health score
        health_score = self._calculate_health_score(damages, tree_confidence)
        
        # =============================================================================
        # ML OUTPUT DATA STRUCTURE
        # =============================================================================
        # Add new fields here when ML model is updated
        # All fields are optional and nullable in the database
        
        results = {
            # Core ML outputs
            'tree_type': tree_type.value,
            'tree_type_confidence': round(tree_confidence, 3),
            'damages_detected': damages,
            'overall_health_score': round(health_score, 3),
            
            # Metadata
            'analysis_timestamp': time.time(),
            
            # Add new ML output fields here:
            # 'new_field': new_value,
            # 'additional_analysis': additional_data,
        }
        
        return results
    
    def _select_tree_type(self) -> TreeType:
        """Select tree type based on probabilities"""
        rand = random.random()
        cumulative = 0.0
        
        for tree_type, probability in self.config.TREE_TYPE_PROBABILITIES.items():
            cumulative += probability
            if rand <= cumulative:
                return tree_type
        
        return TreeType.UNKNOWN

    def _generate_damage_analysis(self) -> List[Dict]:
        """Generate mock damage analysis"""
        damages = []
        
        # Select number of damages based on probabilities
        num_damages = self._select_damage_count()
        
        if num_damages == 0:
            return damages
        
        # Select damage types based on probabilities
        selected_damages = self._select_damage_types(num_damages)
        
        for damage_type in selected_damages:
            confidence = random.uniform(*self.config.DAMAGE_CONFIDENCE_RANGE)
            severity = self._select_severity()
            
            damage_info = {
                'type': damage_type.value,
                'confidence': round(confidence, 3),
                'severity': severity,
                'description': self.config.DAMAGE_DESCRIPTIONS.get(damage_type, "Unknown damage type"),
                'recommendations': self.config.TREATMENT_RECOMMENDATIONS.get(damage_type, {}).get(severity, ["Consult with arborist"])
            }
            damages.append(damage_info)
        
        return damages

    def _select_damage_count(self) -> int:
        """Select number of damages based on probabilities"""
        rand = random.random()
        cumulative = 0.0
        
        for count, probability in self.config.DAMAGE_COUNT_PROBABILITIES.items():
            cumulative += probability
            if rand <= cumulative:
                return count
        
        return 0

    def _select_damage_types(self, count: int) -> List[DamageType]:
        """Select damage types based on probabilities"""
        damage_types = list(self.config.DAMAGE_TYPE_PROBABILITIES.keys())
        probabilities = list(self.config.DAMAGE_TYPE_PROBABILITIES.values())
        
        selected = []
        for _ in range(count):
            damage_type = random.choices(damage_types, weights=probabilities)[0]
            if damage_type not in selected:
                selected.append(damage_type)
        
        return selected

    def _select_severity(self) -> str:
        """Select severity based on probabilities"""
        rand = random.random()
        cumulative = 0.0
        
        for severity, probability in self.config.SEVERITY_PROBABILITIES.items():
            cumulative += probability
            if rand <= cumulative:
                return severity
        
        return 'low'
    
    def _calculate_health_score(self, damages: List[Dict], tree_confidence: float) -> float:
        """Calculate overall health score based on damages and confidence"""
        base_score = tree_confidence
        
        # Reduce score based on damage severity
        for damage in damages:
            severity = damage['severity']
            modifier = self.config.HEALTH_SCORE_MODIFIERS.get(severity, 1.0)
            base_score *= modifier
        
        # Add some randomness
        health_score = base_score * random.uniform(0.9, 1.1)
        return max(0.0, min(1.0, health_score))


# Global instance
ml_analyzer = MLTreeAnalyzer()


def analyze_tree_image(image_path: str, additional_params: Dict = None) -> Dict:
    """
    Convenience function for tree analysis
    
    Args:
        image_path: Path to the tree image
        additional_params: Additional parameters for analysis
        
    Returns:
        Dict with analysis results
    """
    return ml_analyzer.analyze_tree(image_path, additional_params)
