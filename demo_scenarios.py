"""
Demonstration of different user scenarios
Shows how the XAI system adapts to different profiles
"""
from main import HealthFitnessXAISystem


def print_separator():
    print("\n" + "=" * 80 + "\n")


def demo_scenario(system, user_data, scenario_name):
    """Demonstrate a specific user scenario"""
    print(f"SCENARIO: {scenario_name}")
    print("-" * 80)
    
    # Create user
    user = system.create_user(user_data)
    
    # Print profile
    print(f"User: {user.name}")
    print(f"Age: {user.age}, Gender: {user.gender}")
    print(f"Weight: {user.weight}kg, Height: {user.height}cm")
    print(f"BMI: {user.bmi} ({user.get_bmi_category()})")
    print(f"Activity Level: {user.activity_level.replace('_', ' ').title()}")
    print(f"Goal: {user.fitness_goals[0].replace('_', ' ').title()}")
    
    # Generate plan
    plan = system.generate_complete_plan(user.user_id)
    
    # Print key recommendations
    print(f"\nKEY RECOMMENDATIONS:")
    print(f"  Daily Calories: {plan['diet_plan']['calorie_target']}")
    print(f"  Protein: {plan['diet_plan']['macro_distribution']['protein_g']}g")
    print(f"  Exercise Split: {plan['exercise_plan']['exercise_split']['cardio_percent']}% Cardio, "
          f"{plan['exercise_plan']['exercise_split']['strength_percent']}% Strength")
    print(f"  Weekly Calorie Burn: {plan['exercise_plan']['expected_weekly_calorie_burn']}")
    
    # Print XAI explanation
    print(f"\nXAI EXPLANATION:")
    print(f"  {plan['diet_plan']['explanations']['calorie_explanation'][2]}")
    
    # Print expected outcome
    outcome = plan['overall_summary']['expected_outcomes']
    print(f"\nEXPECTED OUTCOME (4 weeks):")
    print(f"  {outcome['expected_weight_change']}")
    print(f"  Confidence: {outcome['confidence']}")
    
    print_separator()


def main():
    """Run demonstration scenarios"""
    system = HealthFitnessXAISystem()
    
    print("=" * 80)
    print("HEALTH & FITNESS XAI SYSTEM - SCENARIO DEMONSTRATIONS")
    print("=" * 80)
    print("\nThis demo shows how the system adapts recommendations for different users")
    print("using Explainable AI to provide transparent, trustworthy guidance.")
    print_separator()
    
    # Scenario 1: Overweight male seeking weight loss
    demo_scenario(
        system,
        {
            'user_id': 'demo1',
            'name': 'John (Overweight)',
            'age': 35,
            'gender': 'male',
            'weight': 95,
            'height': 175,
            'activity_level': 'lightly_active',
            'fitness_goals': ['weight_loss'],
            'dietary_restrictions': [],
            'medical_conditions': []
        },
        "Overweight Male - Weight Loss Goal"
    )
    
    # Scenario 2: Young female seeking muscle gain
    demo_scenario(
        system,
        {
            'user_id': 'demo2',
            'name': 'Sarah (Athlete)',
            'age': 24,
            'gender': 'female',
            'weight': 58,
            'height': 165,
            'activity_level': 'very_active',
            'fitness_goals': ['muscle_gain'],
            'dietary_restrictions': [],
            'medical_conditions': []
        },
        "Young Female - Muscle Gain Goal"
    )
    
    # Scenario 3: Sedentary worker seeking fitness
    demo_scenario(
        system,
        {
            'user_id': 'demo3',
            'name': 'Mike (Office Worker)',
            'age': 42,
            'gender': 'male',
            'weight': 78,
            'height': 180,
            'activity_level': 'sedentary',
            'fitness_goals': ['maintenance'],
            'dietary_restrictions': [],
            'medical_conditions': []
        },
        "Sedentary Office Worker - Maintenance Goal"
    )
    
    # Scenario 4: Endurance athlete
    demo_scenario(
        system,
        {
            'user_id': 'demo4',
            'name': 'Lisa (Runner)',
            'age': 29,
            'gender': 'female',
            'weight': 55,
            'height': 168,
            'activity_level': 'extra_active',
            'fitness_goals': ['endurance'],
            'dietary_restrictions': ['vegetarian'],
            'medical_conditions': []
        },
        "Endurance Runner - Performance Goal"
    )
    
    # Scenario 5: Senior seeking health improvement
    demo_scenario(
        system,
        {
            'user_id': 'demo5',
            'name': 'Robert (Senior)',
            'age': 62,
            'gender': 'male',
            'weight': 82,
            'height': 172,
            'activity_level': 'lightly_active',
            'fitness_goals': ['weight_loss'],
            'dietary_restrictions': [],
            'medical_conditions': []
        },
        "Senior Citizen - Health Improvement"
    )
    
    # Scenario 6: Underweight person seeking healthy weight
    demo_scenario(
        system,
        {
            'user_id': 'demo6',
            'name': 'Emma (Underweight)',
            'age': 21,
            'gender': 'female',
            'weight': 48,
            'height': 170,
            'activity_level': 'moderately_active',
            'fitness_goals': ['muscle_gain'],
            'dietary_restrictions': ['vegan'],
            'medical_conditions': []
        },
        "Underweight Female - Healthy Weight Gain"
    )
    
    print("\nDEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKEY OBSERVATIONS:")
    print("1. Each user receives a personalized plan based on their unique profile")
    print("2. Calorie targets vary based on TDEE, activity level, and goals")
    print("3. Exercise splits adapt to goals (cardio for weight loss, strength for muscle)")
    print("4. XAI provides clear explanations for every recommendation")
    print("5. The system considers age, BMI, and activity level in its recommendations")
    print("\nThis demonstrates how Explainable AI builds trust through transparency!")


if __name__ == "__main__":
    main()
