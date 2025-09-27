from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TreeType(str, enum.Enum):
    OAK = "oak"
    PINE = "pine"
    BIRCH = "birch"
    MAPLE = "maple"
    CHERRY = "cherry"
    UNKNOWN = "unknown"


class DamageType(str, enum.Enum):
    INSECT_DAMAGE = "insect_damage"
    FUNGAL_INFECTION = "fungal_infection"
    BARK_DAMAGE = "bark_damage"
    LEAF_DISCOLORATION = "leaf_discoloration"
    BRANCH_BREAKAGE = "branch_breakage"
    ROOT_DAMAGE = "root_damage"
    DROUGHT_STRESS = "drought_stress"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    original_path = Column(String(500), nullable=False)
    result_path = Column(String(500), nullable=True)
    
    # ML Analysis Results
    tree_type = Column(Enum(TreeType), nullable=True)
    tree_type_confidence = Column(Float, nullable=True)
    damages_detected = Column(Text, nullable=True)  # JSON string with damage analysis
    overall_health_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Legacy field for backward compatibility
    task_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="tasks")
