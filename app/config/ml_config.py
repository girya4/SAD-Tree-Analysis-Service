"""
ML Configuration for Tree Analysis
Easy to modify mock results and behavior
"""
from typing import Dict, List, Tuple
from app.models.task import TreeType, DamageType


class MLConfig:
    """Configuration for ML tree analysis mock"""
    
    # Processing time range (seconds)
    PROCESSING_TIME_RANGE = (5, 25)
    
    # Confidence ranges
    TREE_CONFIDENCE_RANGE = (0.65, 0.95)
    DAMAGE_CONFIDENCE_RANGE = (0.45, 0.90)
    HEALTH_SCORE_RANGE = (0.3, 0.9)
    
    # Tree type probabilities (can be modified to change distribution)
    TREE_TYPE_PROBABILITIES = {
        TreeType.OAK: 0.25,
        TreeType.PINE: 0.20,
        TreeType.BIRCH: 0.15,
        TreeType.MAPLE: 0.15,
        TreeType.CHERRY: 0.10,
        TreeType.UNKNOWN: 0.15
    }
    
    # Damage type probabilities
    DAMAGE_TYPE_PROBABILITIES = {
        DamageType.INSECT_DAMAGE: 0.20,
        DamageType.FUNGAL_INFECTION: 0.15,
        DamageType.BARK_DAMAGE: 0.18,
        DamageType.LEAF_DISCOLORATION: 0.12,
        DamageType.BRANCH_BREAKAGE: 0.10,
        DamageType.ROOT_DAMAGE: 0.08,
        DamageType.DROUGHT_STRESS: 0.10,
        DamageType.NUTRIENT_DEFICIENCY: 0.07
    }
    
    # Severity probabilities
    SEVERITY_PROBABILITIES = {
        'low': 0.50,
        'medium': 0.35,
        'high': 0.15
    }
    
    # Number of damages per tree (0-4)
    DAMAGE_COUNT_PROBABILITIES = {
        0: 0.30,  # 30% chance of no damage
        1: 0.35,  # 35% chance of 1 damage
        2: 0.20,  # 20% chance of 2 damages
        3: 0.10,  # 10% chance of 3 damages
        4: 0.05   # 5% chance of 4 damages
    }
    
    # Health score modifiers based on damage severity
    HEALTH_SCORE_MODIFIERS = {
        'low': 0.95,
        'medium': 0.85,
        'high': 0.70
    }
    
    # ML Model version
    ML_MODEL_VERSION = "mock_v2.0"
    
    # Tree type descriptions
    TREE_TYPE_DESCRIPTIONS = {
        TreeType.OAK: "Mighty oak tree with strong branches and deep roots",
        TreeType.PINE: "Evergreen pine tree with needle-like leaves",
        TreeType.BIRCH: "Elegant birch tree with distinctive white bark",
        TreeType.MAPLE: "Beautiful maple tree known for its colorful leaves",
        TreeType.CHERRY: "Ornamental cherry tree with delicate blossoms",
        TreeType.UNKNOWN: "Tree species not recognized by the model"
    }
    
    # Damage descriptions
    DAMAGE_DESCRIPTIONS = {
        DamageType.INSECT_DAMAGE: "Signs of insect infestation detected",
        DamageType.FUNGAL_INFECTION: "Fungal infection present on tree",
        DamageType.BARK_DAMAGE: "Bark damage or wounds observed",
        DamageType.LEAF_DISCOLORATION: "Unusual leaf discoloration detected",
        DamageType.BRANCH_BREAKAGE: "Broken or damaged branches found",
        DamageType.ROOT_DAMAGE: "Potential root system damage",
        DamageType.DROUGHT_STRESS: "Signs of drought stress visible",
        DamageType.NUTRIENT_DEFICIENCY: "Nutrient deficiency symptoms detected"
    }
    
    # Treatment recommendations
    TREATMENT_RECOMMENDATIONS = {
        DamageType.INSECT_DAMAGE: {
            'low': ["Monitor tree regularly", "Apply preventive treatment"],
            'medium': ["Apply insecticide treatment", "Remove affected branches"],
            'high': ["Immediate treatment required", "Consult arborist", "Consider tree removal if severe"]
        },
        DamageType.FUNGAL_INFECTION: {
            'low': ["Improve air circulation", "Remove dead material"],
            'medium': ["Apply fungicide", "Prune affected areas"],
            'high': ["Immediate fungicide treatment", "Extensive pruning required", "Monitor closely"]
        },
        DamageType.BARK_DAMAGE: {
            'low': ["Protect from further damage", "Apply wound dressing"],
            'medium': ["Clean and treat wounds", "Monitor for infection"],
            'high': ["Immediate wound treatment", "Protect from pests", "Consider professional help"]
        },
        DamageType.LEAF_DISCOLORATION: {
            'low': ["Check soil conditions", "Adjust watering"],
            'medium': ["Soil testing recommended", "Fertilizer application"],
            'high': ["Immediate soil analysis", "Professional consultation needed"]
        },
        DamageType.BRANCH_BREAKAGE: {
            'low': ["Prune broken branches", "Clean cuts properly"],
            'medium': ["Remove damaged branches", "Support remaining structure"],
            'high': ["Immediate pruning required", "Structural support needed", "Safety assessment"]
        },
        DamageType.ROOT_DAMAGE: {
            'low': ["Improve drainage", "Avoid soil compaction"],
            'medium': ["Root zone treatment", "Mulching recommended"],
            'high': ["Immediate root care", "Professional assessment", "Consider tree removal"]
        },
        DamageType.DROUGHT_STRESS: {
            'low': ["Increase watering", "Apply mulch"],
            'medium': ["Deep watering schedule", "Soil moisture monitoring"],
            'high': ["Emergency watering", "Shade protection", "Professional irrigation"]
        },
        DamageType.NUTRIENT_DEFICIENCY: {
            'low': ["Soil testing", "Balanced fertilization"],
            'medium': ["Targeted nutrient application", "pH adjustment"],
            'high': ["Immediate nutrient treatment", "Soil amendment", "Professional consultation"]
        }
    }


# Global configuration instance
ml_config = MLConfig()
