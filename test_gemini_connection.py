"""Test script to verify Gemini API connection"""
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def print_section(title, char='=', length=50):
    """Print a section header"""
    print(f"\n{char * length}")
    print(f" {title} ".center(length, char))
    print(f"{char * length}\n")

def test_connection():
    """Test connection to Gemini API"""
    # Set console encoding to UTF-8 for Windows
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    print_section("API KEY VERIFICATION")
    print(f"API Key: {'*' * 10 + api_key[-4:] if api_key else 'Not found'}")
    
    if not api_key or api_key == 'your_api_key_here':
        print("\n[ERROR] Please set your GOOGLE_API_KEY in the .env file")
        print("Get an API key from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        # Configure the API
        print_section("TESTING CONNECTION")
        print("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        
        # Test listing models
        print("Fetching available models...")
        models = genai.list_models()
        
        # Print available models
        print_section("CONNECTION SUCCESSFUL")
        print("Successfully connected to Gemini API!")
        
        print_section("AVAILABLE MODELS")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model.name}")
            
        # Test model generation
        print_section("TESTING MODEL GENERATION")
        model = genai.GenerativeModel('gemini-pro')
        print("Sending test request to Gemini Pro...")
        response = model.generate_content("Hello, Gemini! Respond with 'Connection successful!'")
        print(f"\nResponse: {response.text}")
        
        return True
        
    except Exception as e:
        print_section("CONNECTION FAILED")
        print(f"Error: {str(e)}")
        
        print_section("TROUBLESHOOTING STEPS")
        print("1. Verify your internet connection")
        print("2. Check if the API key is valid and has access to the Gemini API")
        print("3. Make sure you've enabled the Gemini API in Google AI Studio")
        print("4. Try generating a new API key from: https://makersuite.google.com/app/apikey")
        print("5. Ensure your system clock is synchronized")
        print("6. Check if there are any firewall or proxy settings blocking the connection")
        
        # Check for specific common errors
        if "quota" in str(e).lower():
            print("\n[NOTE] You might have exceeded your API quota. Check your usage at:")
            print("https://aistudio.google.com/app/apikey")
            
        return False

if __name__ == "__main__":
    test_connection()
