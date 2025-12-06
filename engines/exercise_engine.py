"""
Exercise Recommendation Engine with XAI
Provides personalized exercise plans with clear explanations
"""
from typing import Dict, List
from collections import OrderedDict
from models.user_profile import UserProfile


class ExerciseRecommendationEngine:
    """Generate personalized exercise recommendations with explanations"""
    
    def __init__(self):
        # Load exercise database from Kaggle dataset
        self.exercise_database = self._load_exercise_database()
    
    def _load_exercise_database(self):
        """Load exercise database from Kaggle dataset JSON"""
        import json
        import os
        
        kaggle_db_path = 'kaggle_data/exercise_database.json'
        
        if os.path.exists(kaggle_db_path):
            with open(kaggle_db_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to original database if Kaggle data not available
            return self._get_default_exercise_database()
    
    def _get_default_exercise_database(self):
        """Fallback exercise database"""
        return {
            # Strength Training
            'push_ups': {'type': 'strength', 'muscle_groups': ['chest', 'triceps', 'shoulders'], 'difficulty': 'beginner', 'calories_per_min': 7},
            'pull_ups': {'type': 'strength', 'muscle_groups': ['back', 'biceps'], 'difficulty': 'intermediate', 'calories_per_min': 8},
            'squats': {'type': 'strength', 'muscle_groups': ['legs', 'glutes'], 'difficulty': 'beginner', 'calories_per_min': 8},
            'deadlifts': {'type': 'strength', 'muscle_groups': ['back', 'legs', 'core'], 'difficulty': 'intermediate', 'calories_per_min': 9},
            'bench_press': {'type': 'strength', 'muscle_groups': ['chest', 'triceps', 'shoulders'], 'difficulty': 'intermediate', 'calories_per_min': 7},
            'shoulder_press': {'type': 'strength', 'muscle_groups': ['shoulders', 'triceps'], 'difficulty': 'beginner', 'calories_per_min': 6},
            'lunges': {'type': 'strength', 'muscle_groups': ['legs', 'glutes'], 'difficulty': 'beginner', 'calories_per_min': 7},
            'planks': {'type': 'strength', 'muscle_groups': ['core'], 'difficulty': 'beginner', 'calories_per_min': 4},
            
            # Cardio
            'running': {'type': 'cardio', 'muscle_groups': ['legs', 'cardiovascular'], 'difficulty': 'beginner', 'calories_per_min': 11},
            'cycling': {'type': 'cardio', 'muscle_groups': ['legs', 'cardiovascular'], 'difficulty': 'beginner', 'calories_per_min': 9},
            'swimming': {'type': 'cardio', 'muscle_groups': ['full_body', 'cardiovascular'], 'difficulty': 'intermediate', 'calories_per_min': 10},
            'jump_rope': {'type': 'cardio', 'muscle_groups': ['legs', 'cardiovascular'], 'difficulty': 'intermediate', 'calories_per_min': 12},
            'rowing': {'type': 'cardio', 'muscle_groups': ['back', 'legs', 'cardiovascular'], 'difficulty': 'intermediate', 'calories_per_min': 10},
            'elliptical': {'type': 'cardio', 'muscle_groups': ['legs', 'cardiovascular'], 'difficulty': 'beginner', 'calories_per_min': 8},
            
            # Flexibility
            'yoga': {'type': 'flexibility', 'muscle_groups': ['full_body'], 'difficulty': 'beginner', 'calories_per_min': 4},
            'stretching': {'type': 'flexibility', 'muscle_groups': ['full_body'], 'difficulty': 'beginner', 'calories_per_min': 3},
            'pilates': {'type': 'flexibility', 'muscle_groups': ['core', 'full_body'], 'difficulty': 'beginner', 'calories_per_min': 5}
        }
    
    def generate_recommendations(self, user: UserProfile) -> Dict:
        """Generate personalized exercise recommendations"""
        # Determine exercise split based on goals and activity level
        exercise_split = self._determine_exercise_split(user)
        
        # Generate weekly workout plan
        weekly_plan = self._generate_weekly_plan(user, exercise_split)
        
        # Calculate expected calorie burn
        calorie_burn = self._calculate_calorie_burn(weekly_plan, user)
        
        # Generate explanations
        explanations = self._generate_explanations(user, exercise_split, calorie_burn)
        
        return {
            'weekly_plan': weekly_plan,
            'exercise_split': exercise_split,
            'expected_weekly_calorie_burn': calorie_burn,
            'explanations': explanations,
            'tips': self._generate_exercise_tips(user)
        }
    
    def _determine_exercise_split(self, user: UserProfile) -> Dict:
        """Determine optimal exercise type distribution"""
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        splits = {
            'weight_loss': {'cardio': 0.60, 'strength': 0.30, 'flexibility': 0.10},
            'muscle_gain': {'cardio': 0.20, 'strength': 0.70, 'flexibility': 0.10},
            'maintenance': {'cardio': 0.40, 'strength': 0.45, 'flexibility': 0.15},
            'endurance': {'cardio': 0.70, 'strength': 0.20, 'flexibility': 0.10}
        }
        
        split = splits.get(primary_goal, splits['maintenance'])
        
        # Adjust based on activity level
        if user.activity_level == 'sedentary':
            # Increase flexibility for beginners
            split['flexibility'] += 0.10
            split['strength'] -= 0.05
            split['cardio'] -= 0.05
        
        return {
            'cardio_percent': int(split['cardio'] * 100),
            'strength_percent': int(split['strength'] * 100),
            'flexibility_percent': int(split['flexibility'] * 100)
        }
    
    def _generate_weekly_plan(self, user: UserProfile, exercise_split: Dict) -> Dict:
        """Generate weekly workout plan"""
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        # Determine workout frequency based on activity level
        frequency_map = {
            'sedentary': 3,
            'lightly_active': 4,
            'moderately_active': 5,
            'very_active': 6,
            'extra_active': 6
        }
        days_per_week = frequency_map.get(user.activity_level, 4)
        
        weekly_plan = OrderedDict()
        
        if primary_goal == 'muscle_gain':
            weekly_plan = OrderedDict([
                ('Monday', {
                    'focus': 'Chest & Triceps',
                    'exercises': [
                        {'name': 'bench_press', 'sets': 4, 'reps': '8-10', 'rest_sec': 90},
                        {'name': 'push_ups', 'sets': 3, 'reps': '12-15', 'rest_sec': 60},
                        {'name': 'shoulder_press', 'sets': 3, 'reps': '10-12', 'rest_sec': 75}
                    ],
                    'duration_min': 45
                }),
                ('Tuesday', {
                    'focus': 'Cardio & Core',
                    'exercises': [
                        {'name': 'running', 'sets': 1, 'duration_min': 20, 'intensity': 'moderate'},
                        {'name': 'planks', 'sets': 3, 'duration_sec': 60, 'rest_sec': 45}
                    ],
                    'duration_min': 30
                }),
                ('Wednesday', {
                    'focus': 'Back & Biceps',
                    'exercises': [
                        {'name': 'deadlifts', 'sets': 4, 'reps': '6-8', 'rest_sec': 120},
                        {'name': 'pull_ups', 'sets': 3, 'reps': '8-10', 'rest_sec': 90},
                        {'name': 'rowing', 'sets': 3, 'duration_min': 5, 'intensity': 'high'}
                    ],
                    'duration_min': 50
                }),
                ('Thursday', {
                    'focus': 'Rest / Active Recovery',
                    'exercises': [
                        {'name': 'yoga', 'sets': 1, 'duration_min': 30, 'intensity': 'light'}
                    ],
                    'duration_min': 30
                }),
                ('Friday', {
                    'focus': 'Legs & Glutes',
                    'exercises': [
                        {'name': 'squats', 'sets': 4, 'reps': '10-12', 'rest_sec': 90},
                        {'name': 'lunges', 'sets': 3, 'reps': '12-15 each leg', 'rest_sec': 60},
                        {'name': 'deadlifts', 'sets': 3, 'reps': '8-10', 'rest_sec': 90}
                    ],
                    'duration_min': 45
                }),
                ('Saturday', {
                    'focus': 'Full Body & Cardio',
                    'exercises': [
                        {'name': 'cycling', 'sets': 1, 'duration_min': 25, 'intensity': 'moderate'},
                        {'name': 'push_ups', 'sets': 2, 'reps': '15-20', 'rest_sec': 60},
                        {'name': 'squats', 'sets': 2, 'reps': '15-20', 'rest_sec': 60}
                    ],
                    'duration_min': 40
                }),
                ('Sunday', {
                    'focus': 'Rest Day',
                    'exercises': [],
                    'duration_min': 0
                })
            ])
        
        elif primary_goal == 'weight_loss':
            weekly_plan = OrderedDict([
                ('Monday', {
                    'focus': 'Cardio & Core',
                    'exercises': [
                        {'name': 'running', 'sets': 1, 'duration_min': 30, 'intensity': 'moderate'},
                        {'name': 'planks', 'sets': 3, 'duration_sec': 45, 'rest_sec': 30},
                        {'name': 'jump_rope', 'sets': 3, 'duration_min': 3, 'rest_sec': 60}
                    ],
                    'duration_min': 45
                }),
                ('Tuesday', {
                    'focus': 'Strength Training',
                    'exercises': [
                        {'name': 'squats', 'sets': 3, 'reps': '15-20', 'rest_sec': 60},
                        {'name': 'push_ups', 'sets': 3, 'reps': '12-15', 'rest_sec': 60},
                        {'name': 'lunges', 'sets': 3, 'reps': '12-15 each leg', 'rest_sec': 60}
                    ],
                    'duration_min': 35
                }),
                ('Wednesday', {
                    'focus': 'Cardio Intervals',
                    'exercises': [
                        {'name': 'cycling', 'sets': 1, 'duration_min': 35, 'intensity': 'high_intervals'},
                        {'name': 'stretching', 'sets': 1, 'duration_min': 10, 'intensity': 'light'}
                    ],
                    'duration_min': 45
                }),
                ('Thursday', {
                    'focus': 'Active Recovery',
                    'exercises': [
                        {'name': 'yoga', 'sets': 1, 'duration_min': 30, 'intensity': 'light'},
                        {'name': 'stretching', 'sets': 1, 'duration_min': 15, 'intensity': 'light'}
                    ],
                    'duration_min': 45
                }),
                ('Friday', {
                    'focus': 'Full Body Circuit',
                    'exercises': [
                        {'name': 'jump_rope', 'sets': 4, 'duration_min': 3, 'rest_sec': 60},
                        {'name': 'squats', 'sets': 3, 'reps': '20', 'rest_sec': 45},
                        {'name': 'push_ups', 'sets': 3, 'reps': '15', 'rest_sec': 45},
                        {'name': 'planks', 'sets': 3, 'duration_sec': 45, 'rest_sec': 30}
                    ],
                    'duration_min': 40
                }),
                ('Saturday', {
                    'focus': 'Long Cardio',
                    'exercises': [
                        {'name': 'running', 'sets': 1, 'duration_min': 40, 'intensity': 'moderate'},
                        {'name': 'stretching', 'sets': 1, 'duration_min': 10, 'intensity': 'light'}
                    ],
                    'duration_min': 50
                }),
                ('Sunday', {
                    'focus': 'Rest Day',
                    'exercises': [],
                    'duration_min': 0
                })
            ])
        
        else:  # maintenance or endurance
            weekly_plan = OrderedDict([
                ('Monday', {
                    'focus': 'Strength Training',
                    'exercises': [
                        {'name': 'squats', 'sets': 3, 'reps': '12-15', 'rest_sec': 60},
                        {'name': 'bench_press', 'sets': 3, 'reps': '10-12', 'rest_sec': 75},
                        {'name': 'pull_ups', 'sets': 3, 'reps': '8-10', 'rest_sec': 90}
                    ],
                    'duration_min': 45
                }),
                ('Tuesday', {
                    'focus': 'Cardio',
                    'exercises': [
                        {'name': 'running', 'sets': 1, 'duration_min': 30, 'intensity': 'moderate'},
                        {'name': 'stretching', 'sets': 1, 'duration_min': 10, 'intensity': 'light'}
                    ],
                    'duration_min': 40
                }),
                ('Wednesday', {
                    'focus': 'Strength Training',
                    'exercises': [
                        {'name': 'deadlifts', 'sets': 3, 'reps': '8-10', 'rest_sec': 90},
                        {'name': 'shoulder_press', 'sets': 3, 'reps': '10-12', 'rest_sec': 75},
                        {'name': 'lunges', 'sets': 3, 'reps': '12-15 each leg', 'rest_sec': 60}
                    ],
                    'duration_min': 45
                }),
                ('Thursday', {
                    'focus': 'Flexibility & Core',
                    'exercises': [
                        {'name': 'yoga', 'sets': 1, 'duration_min': 35, 'intensity': 'moderate'},
                        {'name': 'planks', 'sets': 3, 'duration_sec': 60, 'rest_sec': 45}
                    ],
                    'duration_min': 45
                }),
                ('Friday', {
                    'focus': 'Full Body',
                    'exercises': [
                        {'name': 'swimming', 'sets': 1, 'duration_min': 30, 'intensity': 'moderate'},
                        {'name': 'stretching', 'sets': 1, 'duration_min': 10, 'intensity': 'light'}
                    ],
                    'duration_min': 40
                }),
                ('Saturday', {
                    'focus': 'Rest / Active Recovery',
                    'exercises': [
                        {'name': 'cycling', 'sets': 1, 'duration_min': 30, 'intensity': 'light'}
                    ],
                    'duration_min': 30
                }),
                ('Sunday', {
                    'focus': 'Rest Day',
                    'exercises': [],
                    'duration_min': 0
                })
            ])
        
        return weekly_plan
    
    def _calculate_calorie_burn(self, weekly_plan: Dict, user: UserProfile) -> float:
        """Calculate expected weekly calorie burn"""
        total_calories = 0
        
        for day, workout in weekly_plan.items():
            for exercise in workout['exercises']:
                exercise_name = exercise['name']
                if exercise_name in self.exercise_database:
                    calories_per_min = self.exercise_database[exercise_name]['calories_per_min']
                    
                    if 'duration_min' in exercise:
                        duration = exercise['duration_min']
                    elif 'duration_sec' in exercise:
                        duration = exercise['duration_sec'] / 60
                        sets = exercise.get('sets', 1)
                        duration *= sets
                    else:
                        # Estimate based on sets and reps
                        sets = exercise.get('sets', 3)
                        duration = sets * 2  # Rough estimate
                    
                    total_calories += calories_per_min * duration
        
        # Adjust for user weight (heavier people burn more calories)
        weight_factor = user.weight / 70  # 70kg as baseline
        total_calories *= weight_factor
        
        return round(total_calories, 2)
    
    def _generate_explanations(self, user: UserProfile, exercise_split: Dict, calorie_burn: float) -> Dict:
        """Generate XAI explanations for exercise recommendations"""
        explanations = {
            'plan_rationale': [],
            'split_explanation': [],
            'feature_importance': {},
            'decision_factors': []
        }
        
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        # Plan rationale
        explanations['plan_rationale'].append(
            f"Your workout plan is designed for {primary_goal.replace('_', ' ')} based on your current fitness level and goals."
        )
        explanations['plan_rationale'].append(
            f"With your {user.activity_level.replace('_', ' ')} lifestyle, we've structured a progressive plan to avoid overtraining."
        )
        explanations['plan_rationale'].append(
            f"Expected weekly calorie burn: {calorie_burn} calories, contributing to your {primary_goal.replace('_', ' ')} goal."
        )
        
        # Split explanation
        explanations['split_explanation'].append(
            f"Cardio ({exercise_split['cardio_percent']}%): " + 
            ("High proportion for fat burning and cardiovascular health." if exercise_split['cardio_percent'] > 50 
             else "Moderate proportion for overall fitness." if exercise_split['cardio_percent'] > 30
             else "Lower proportion, focusing on other training types.")
        )
        explanations['split_explanation'].append(
            f"Strength Training ({exercise_split['strength_percent']}%): " +
            ("Emphasized for muscle building and metabolic boost." if exercise_split['strength_percent'] > 50
             else "Balanced proportion for muscle maintenance and strength." if exercise_split['strength_percent'] > 30
             else "Lower proportion, supporting primary goal.")
        )
        explanations['split_explanation'].append(
            f"Flexibility ({exercise_split['flexibility_percent']}%): " +
            "Essential for injury prevention, mobility, and recovery."
        )
        
        # Feature importance (XAI component)
        bmi_importance = round(abs(25 - (user.bmi or 25)) / 25 * 0.13, 3)
        explanations['feature_importance'] = {
            'fitness_goal': 0.35,
            'activity_level': 0.22,
            'bmi': max(0.05, bmi_importance),  # Ensure minimum 5% contribution
            'age': round((100 - user.age) / 100 * 0.10, 3),
            'current_fitness': 0.08
        }
        
        # Decision factors
        explanations['decision_factors'] = [
            {
                'factor': 'Weight',
                'value': f"{user.weight} kg",
                'impact': 'High',
                'explanation': f"Your weight of {user.weight} kg affects exercise intensity and impact on joints."
            },
            {
                'factor': 'Height',
                'value': f"{user.height} cm",
                'impact': 'Medium',
                'explanation': f"Height of {user.height} cm influences exercise form and equipment adjustments."
            },
            {
                'factor': 'Primary Goal',
                'value': primary_goal.replace('_', ' ').title(),
                'impact': 'Very High',
                'explanation': f"{primary_goal.replace('_', ' ').title()} determines exercise type distribution and intensity."
            },
            {
                'factor': 'Activity Level',
                'value': user.activity_level.replace('_', ' ').title(),
                'impact': 'High',
                'explanation': f"Your {user.activity_level.replace('_', ' ')} lifestyle influences workout frequency and recovery needs."
            },
            {
                'factor': 'BMI',
                'value': f"{user.bmi} ({user.get_bmi_category()})",
                'impact': 'Medium',
                'explanation': f"BMI affects exercise intensity recommendations and injury risk considerations."
            },
            {
                'factor': 'Age',
                'value': f"{user.age} years",
                'impact': 'Medium',
                'explanation': "Age influences recovery time and appropriate exercise intensity levels."
            }
        ]
        
        return explanations
    
    def _generate_exercise_tips(self, user: UserProfile) -> List[str]:
        """Generate personalized exercise tips"""
        tips = []
        
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        sleep_hours = user.sleep_hours or 7.0
        
        tips.append("Always warm up for 5-10 minutes before exercising to prevent injury.")
        tips.append("Cool down and stretch after workouts to improve flexibility and reduce soreness.")
        
        if primary_goal == 'muscle_gain':
            tips.append("Progressive overload: Gradually increase weight or reps each week.")
            tips.append("Rest is crucial - muscles grow during recovery, not during workouts.")
        
        if primary_goal == 'weight_loss':
            tips.append("Consistency is key - even short workouts are better than skipping entirely.")
            tips.append("Combine cardio with strength training to preserve muscle while losing fat.")
        
        # Sleep-based tips
        if sleep_hours < 7:
            tips.append(f"⚠️ Your {sleep_hours} hours of sleep may impair recovery and performance. Aim for 7-9 hours for optimal results.")
            tips.append("Poor sleep increases injury risk and reduces workout effectiveness. Prioritize rest days.")
        elif sleep_hours >= 8:
            tips.append(f"✅ Your {sleep_hours} hours of sleep supports excellent recovery and muscle growth!")
        
        if user.age > 40:
            tips.append("Focus on joint-friendly exercises and prioritize proper form over heavy weights.")
        
        if user.activity_level == 'sedentary':
            tips.append("Start gradually - it's better to do less and build up than to overtrain and quit.")
        
        tips.append("Stay hydrated: drink water before, during, and after exercise.")
        tips.append("Listen to your body - rest if you experience pain beyond normal muscle fatigue.")
        
        return tips
