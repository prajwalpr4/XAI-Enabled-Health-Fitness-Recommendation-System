"""
Firebase Web Configuration Module
Provides Firebase configuration for client-side initialization
"""
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseWebConfig:
    """Firebase web configuration for client-side initialization"""
    
    @staticmethod
    def get_config():
        """
        Get Firebase web configuration as a dictionary
        
        Returns:
            dict: Firebase configuration for client-side initialization
        """
        return {
            "apiKey": os.getenv("FIREBASE_API_KEY", ""),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL_WEB", ""),
            "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": os.getenv("FIREBASE_APP_ID", ""),
            "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", "")
        }
    
    @staticmethod
    def get_config_json():
        """
        Get Firebase configuration as JSON string
        
        Returns:
            str: Firebase configuration as JSON
        """
        import json
        return json.dumps(FirebaseWebConfig.get_config())
    
    @staticmethod
    def validate_config():
        """
        Validate that all required Firebase configuration is present
        
        Returns:
            tuple: (is_valid, missing_fields)
        """
        config = FirebaseWebConfig.get_config()
        required_fields = [
            "apiKey",
            "authDomain",
            "databaseURL",
            "projectId",
            "storageBucket",
            "messagingSenderId",
            "appId"
        ]
        
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        return len(missing_fields) == 0, missing_fields


# Example usage
if __name__ == "__main__":
    config = FirebaseWebConfig.get_config()
    print("Firebase Web Configuration:")
    print(config)
    
    is_valid, missing = FirebaseWebConfig.validate_config()
    if is_valid:
        print("\n✅ Firebase configuration is valid")
    else:
        print(f"\n❌ Missing configuration fields: {missing}")
