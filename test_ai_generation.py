"""Test script to verify AI advice generation"""
import sys
import io
from dotenv import load_dotenv
from llm_service import GeminiService

# Set console encoding to UTF-8 for Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

# Load environment variables
load_dotenv()

def test_ai_generation():
    """Test AI advice generation"""
    print("\n" + "="*60)
    print(" TESTING AI ADVICE GENERATION ".center(60, "="))
    print("="*60 + "\n")
    
    try:
        # Create a test user profile
        user_profile = {
            'name': 'Test User',
            'age': 30,
            'gender': 'male',
            'weight': 75,
            'height': 180,
            'activity_level': 'moderately_active',
            'fitness_goals': ['weight_loss', 'muscle_gain'],
            'dietary_restrictions': [],
            'medical_conditions': []
        }
        
        # Create context
        context = """
        Current Plan Summary:
        - Goal: Weight Loss & Muscle Gain
        - Daily Calories: 2200
        - Workout Frequency: 4 times per week
        - Dietary Focus: High Protein
        """
        
        print("Initializing Gemini Service...")
        gemini = GeminiService()
        print("[OK] Gemini Service initialized successfully\n")
        
        print("Generating personalized advice...")
        advice = gemini.get_personalized_advice(
            user_profile=user_profile,
            context=context
        )
        
        print("[OK] AI Advice generated successfully!\n")
        print("="*60)
        print(" GENERATED ADVICE ".center(60, "="))
        print("="*60 + "\n")
        print(advice)
        print("\n" + "="*60)
        print(" TEST COMPLETED SUCCESSFULLY ".center(60, "="))
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error: {str(e)}\n")
        print("="*60)
        print(" TROUBLESHOOTING ".center(60, "="))
        print("="*60)
        print("\n1. Check if your API key is valid")
        print("2. Verify your internet connection")
        print("3. Check the .env file for GOOGLE_API_KEY")
        print("4. Ensure the Gemini API is enabled in your Google account")
        print("\n" + "="*60 + "\n")
        return False

if __name__ == "__main__":
    test_ai_generation()
