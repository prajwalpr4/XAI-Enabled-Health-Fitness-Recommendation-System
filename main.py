"""
Main Application - Health & Fitness XAI System
Integrates all components and provides the main interface
"""
from models.user_profile import UserProfile
from engines.diet_engine import DietRecommendationEngine
from engines.exercise_engine import ExerciseRecommendationEngine
from typing import Dict, List, Optional
import json


class HealthFitnessXAISystem:
    """Main system integrating diet and exercise recommendations with XAI"""
    
    def __init__(self):
        self.diet_engine = DietRecommendationEngine()
        self.exercise_engine = ExerciseRecommendationEngine()
        self.users = {}
    
    def create_user(self, user_data: Dict) -> UserProfile:
        """Create a new user profile"""
        user = UserProfile.from_dict(user_data)
        self.users[user.user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, updates: Dict) -> UserProfile:
        """Update user profile"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update fields
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        # Recalculate metrics
        user.__post_init__()
        return user
    
    def generate_complete_plan(self, user_id: str) -> Dict:
        """Generate complete personalized plan with explanations"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Generate recommendations
        diet_plan = self.diet_engine.generate_recommendations(user)
        exercise_plan = self.exercise_engine.generate_recommendations(user)
        
        # Compile complete plan
        complete_plan = {
            'user_profile': user.to_dict(),
            'diet_plan': diet_plan,
            'exercise_plan': exercise_plan,
            'overall_summary': self._generate_overall_summary(user, diet_plan, exercise_plan)
        }
        
        return complete_plan
    
    def _generate_overall_summary(self, user: UserProfile, diet_plan: Dict, exercise_plan: Dict) -> Dict:
        """Generate overall plan summary with key insights"""
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        summary = {
            'overview': f"Personalized {primary_goal.replace('_', ' ')} plan for {user.name}",
            'key_metrics': {
                'bmi': user.bmi,
                'bmi_category': user.get_bmi_category(),
                'daily_calorie_target': diet_plan['calorie_target'],
                'weekly_calorie_burn': exercise_plan['expected_weekly_calorie_burn']
            },
            'expected_outcomes': self._predict_outcomes(user, diet_plan, exercise_plan),
            'success_factors': [
                'Consistency in following the meal plan',
                'Adherence to exercise schedule',
                'Adequate sleep (7-9 hours)',
                'Stress management',
                'Regular progress tracking'
            ],
            'why_this_works': self._explain_plan_effectiveness(user, primary_goal)
        }
        
        return summary
    
    def _predict_outcomes(self, user: UserProfile, diet_plan: Dict, exercise_plan: Dict) -> Dict:
        """Predict expected outcomes with explanations"""
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        # Calculate calorie balance
        daily_intake = diet_plan['calorie_target']
        weekly_burn = exercise_plan['expected_weekly_calorie_burn']
        daily_burn_from_exercise = weekly_burn / 7
        
        daily_balance = daily_intake - (user.tdee + daily_burn_from_exercise)
        weekly_balance = daily_balance * 7
        
        outcomes = {}
        
        if primary_goal == 'weight_loss':
            # 7700 calories = 1 kg of fat
            weekly_weight_change = -(weekly_balance / 7700)
            monthly_weight_change = weekly_weight_change * 4
            
            outcomes = {
                'timeframe': '4 weeks',
                'expected_weight_change': f"{monthly_weight_change:.1f} kg loss",
                'explanation': f"With a daily deficit of {abs(daily_balance):.0f} calories (diet + exercise), you'll lose approximately {weekly_weight_change:.2f} kg/week safely.",
                'confidence': 'High' if 0.5 <= abs(weekly_weight_change) <= 1 else 'Medium',
                'notes': 'Results may vary based on adherence, genetics, and other factors.'
            }
        
        elif primary_goal == 'muscle_gain':
            weekly_weight_change = weekly_balance / 7700
            monthly_weight_change = weekly_weight_change * 4
            
            outcomes = {
                'timeframe': '4 weeks',
                'expected_weight_change': f"{monthly_weight_change:.1f} kg gain",
                'expected_muscle_gain': f"{monthly_weight_change * 0.5:.1f} kg (approximate)",
                'explanation': f"With a daily surplus of {daily_balance:.0f} calories and strength training, you'll gain approximately {weekly_weight_change:.2f} kg/week.",
                'confidence': 'Medium',
                'notes': 'Muscle gain requires time; some weight gain will be muscle, some fat.'
            }
        
        else:
            outcomes = {
                'timeframe': '4 weeks',
                'expected_weight_change': 'Maintenance (±0.5 kg)',
                'explanation': 'Your calorie intake matches expenditure, maintaining current weight while improving fitness.',
                'confidence': 'High',
                'notes': 'Body composition may improve (more muscle, less fat) even at stable weight.'
            }
        
        return outcomes
    
    def _explain_plan_effectiveness(self, user: UserProfile, goal: str) -> List[str]:
        """Explain why this plan is effective for the user"""
        explanations = []
        
        explanations.append(
            f"✓ Personalized Approach: This plan is tailored specifically to your age ({user.age}), "
            f"current weight ({user.weight}kg), height ({user.height}cm), and {user.activity_level.replace('_', ' ')} lifestyle."
        )
        
        explanations.append(
            f"✓ Science-Based Calculations: Using the Mifflin-St Jeor equation, your BMR is {user.bmr} calories. "
            f"Combined with your activity level, your TDEE is {user.tdee} calories - this is the foundation of your plan."
        )
        
        explanations.append(
            f"✓ Balanced Macronutrients: The macro distribution is optimized for {goal.replace('_', ' ')}, "
            "ensuring adequate protein for muscle, carbs for energy, and fats for hormones."
        )
        
        explanations.append(
            "✓ Progressive Exercise Plan: The workout split balances different training types, "
            "allowing for adequate recovery while maximizing results."
        )
        
        explanations.append(
            "✓ Sustainable & Safe: The calorie deficit/surplus is within safe limits (not extreme), "
            "promoting long-term success rather than quick fixes that lead to yo-yo effects."
        )
        
        return explanations
    
    def export_plan(self, user_id: str, format: str = 'json') -> str:
        """Export complete plan to file"""
        plan = self.generate_complete_plan(user_id)
        
        if format == 'json':
            return json.dumps(plan, indent=2, default=str)
        else:
            raise ValueError(f"Format {format} not supported")
    
    def get_progress_tracking_template(self) -> Dict:
        """Provide template for tracking progress"""
        return {
            'weekly_tracking': {
                'weight': 'Record weight every Monday morning',
                'measurements': 'Chest, waist, hips, thighs (bi-weekly)',
                'energy_levels': 'Rate 1-10 daily',
                'workout_completion': 'Track completed vs planned sessions',
                'diet_adherence': 'Track meals followed vs planned'
            },
            'monthly_review': [
                'Review weight/measurement changes',
                'Assess energy and mood improvements',
                'Check strength/endurance progress',
                'Adjust plan if needed based on results'
            ]
        }


def main():
    """Example usage of the system"""
    # Initialize system
    system = HealthFitnessXAISystem()
    
    # Create sample user
    user_data = {
        'user_id': 'user001',
        'name': 'John Doe',
        'age': 30,
        'gender': 'male',
        'weight': 85,
        'height': 175,
        'activity_level': 'moderately_active',
        'medical_conditions': [],
        'dietary_restrictions': [],
        'fitness_goals': ['weight_loss']
    }
    
    user = system.create_user(user_data)
    print(f"Created user: {user.name}")
    print(f"BMI: {user.bmi} ({user.get_bmi_category()})")
    print(f"BMR: {user.bmr} calories")
    print(f"TDEE: {user.tdee} calories")
    print("\n" + "="*80 + "\n")
    
    # Generate complete plan
    complete_plan = system.generate_complete_plan('user001')
    
    # Display results
    print("OVERALL SUMMARY")
    print("-" * 80)
    summary = complete_plan['overall_summary']
    print(f"Goal: {summary['overview']}")
    print(f"\nKey Metrics:")
    for key, value in summary['key_metrics'].items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nExpected Outcomes (4 weeks):")
    outcomes = summary['expected_outcomes']
    for key, value in outcomes.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "="*80 + "\n")
    
    # Diet Plan
    print("DIET PLAN")
    print("-" * 80)
    diet = complete_plan['diet_plan']
    print(f"Daily Calorie Target: {diet['calorie_target']} calories")
    print(f"\nMacronutrient Distribution:")
    macro = diet['macro_distribution']
    print(f"  - Protein: {macro['protein_g']}g ({macro['protein_percent']}%)")
    print(f"  - Carbs: {macro['carbs_g']}g ({macro['carbs_percent']}%)")
    print(f"  - Fats: {macro['fats_g']}g ({macro['fats_percent']}%)")
    
    print(f"\nExplanations:")
    for explanation in diet['explanations']['calorie_explanation']:
        print(f"  • {explanation}")
    
    print(f"\nSample Meal Plan:")
    for meal_type, items in diet['meal_plan']['meals'].items():
        print(f"  {meal_type.upper()}:")
        for item in items:
            print(f"    - {item['food'].replace('_', ' ').title()}: {item['quantity']}{item['unit']}")
    
    print("\n" + "="*80 + "\n")
    
    # Exercise Plan
    print("EXERCISE PLAN")
    print("-" * 80)
    exercise = complete_plan['exercise_plan']
    split = exercise['exercise_split']
    print(f"Exercise Split:")
    print(f"  - Cardio: {split['cardio_percent']}%")
    print(f"  - Strength: {split['strength_percent']}%")
    print(f"  - Flexibility: {split['flexibility_percent']}%")
    
    print(f"\nExpected Weekly Calorie Burn: {exercise['expected_weekly_calorie_burn']} calories")
    
    print(f"\nWeekly Workout Plan:")
    for day, workout in exercise['weekly_plan'].items():
        print(f"\n  {day.upper()} - {workout['focus']} ({workout['duration_min']} min)")
        for ex in workout['exercises']:
            if 'reps' in ex:
                print(f"    - {ex['name'].replace('_', ' ').title()}: {ex['sets']} sets x {ex['reps']} reps")
            elif 'duration_min' in ex:
                print(f"    - {ex['name'].replace('_', ' ').title()}: {ex['duration_min']} minutes")
            elif 'duration_sec' in ex:
                print(f"    - {ex['name'].replace('_', ' ').title()}: {ex['sets']} sets x {ex['duration_sec']} seconds")
    
    print("\n" + "="*80 + "\n")
    
    # Explanations
    print("WHY THIS PLAN WORKS (XAI EXPLANATIONS)")
    print("-" * 80)
    for explanation in summary['why_this_works']:
        print(f"{explanation}\n")
    
    print("\n" + "="*80 + "\n")
    
    # Decision Factors
    print("KEY DECISION FACTORS")
    print("-" * 80)
    for factor in diet['explanations']['decision_factors']:
        print(f"{factor['factor']}: {factor['value']}")
        print(f"  Impact: {factor['impact']}")
        print(f"  Why: {factor['explanation']}\n")


if __name__ == "__main__":
    main()
