"""
User Profile Model
Manages user health and fitness data
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json


@dataclass
class UserProfile:
    """User health and fitness profile"""
    user_id: str
    name: str
    age: int
    gender: str  # 'male', 'female', 'other'
    weight: float  # in kg
    height: float  # in cm
    activity_level: str  # 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'
    
    # Sleep tracking
    sleep_hours: Optional[float] = 7.0  # Average hours of sleep per night
    
    # Optional health metrics
    medical_conditions: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    fitness_goals: List[str] = field(default_factory=list)  # 'weight_loss', 'muscle_gain', 'maintenance', 'endurance'
    
    # Calculated metrics
    bmi: Optional[float] = None
    bmr: Optional[float] = None  # Basal Metabolic Rate
    tdee: Optional[float] = None  # Total Daily Energy Expenditure
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate derived metrics"""
        self.calculate_bmi()
        self.calculate_bmr()
        self.calculate_tdee()
    
    def calculate_bmi(self) -> float:
        """Calculate Body Mass Index"""
        height_m = self.height / 100
        self.bmi = round(self.weight / (height_m ** 2), 2)
        return self.bmi
    
    def calculate_bmr(self) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender.lower() == 'male':
            self.bmr = round(10 * self.weight + 6.25 * self.height - 5 * self.age + 5, 2)
        else:
            self.bmr = round(10 * self.weight + 6.25 * self.height - 5 * self.age - 161, 2)
        return self.bmr
    
    def calculate_tdee(self) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        self.tdee = round(self.bmr * multiplier, 2)
        return self.tdee
    
    def get_bmi_category(self) -> str:
        """Get BMI category"""
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'weight': self.weight,
            'height': self.height,
            'activity_level': self.activity_level,
            'sleep_hours': self.sleep_hours,
            'medical_conditions': self.medical_conditions,
            'dietary_restrictions': self.dietary_restrictions,
            'fitness_goals': self.fitness_goals,
            'bmi': self.bmi,
            'bmr': self.bmr,
            'tdee': self.tdee,
            'bmi_category': self.get_bmi_category()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Create UserProfile from dictionary"""
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            weight=data['weight'],
            height=data['height'],
            activity_level=data['activity_level'],
            sleep_hours=data.get('sleep_hours', 7.0),
            medical_conditions=data.get('medical_conditions', []),
            dietary_restrictions=data.get('dietary_restrictions', []),
            fitness_goals=data.get('fitness_goals', [])
        )
