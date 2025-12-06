"""
Test script to verify AI advice generation
"""
import sys
import os
import io

# Fix encoding issues on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_service import GeminiService

def test_ai_advice():
    """Test AI advice generation"""
    try:
        print("Initializing Gemini Service...")
        gemini = GeminiService()
        print("[OK] Gemini Service initialized successfully")
        
        # Test with sample user profile
        test_profile = {
            'age': 28,
            'gender': 'male',
            'weight': 75,
            'height': 175,
            'activity_level': 'moderately_active',
            'goal': 'weight_loss',
            'dietary_restrictions': ['lactose']
        }
        
        test_context = """
        Current Plan Summary:
        - Goal: weight loss
        - Daily Calories: 1800
        - Workout Frequency: 4 times per week
        - Dietary Focus: High protein, low carb
        """
        
        print("\nGenerating AI advice...")
        advice = gemini.get_personalized_advice(test_profile, test_context)
        
        print("\n" + "="*60)
        print("GENERATED AI ADVICE:")
        print("="*60)
        print(advice)
        print("="*60)
        
        if advice and len(advice) > 50:
            print("\n[OK] AI advice generated successfully!")
            return True
        else:
            print("\n[FAIL] AI advice is too short or empty")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_advice()
    sys.exit(0 if success else 1)
