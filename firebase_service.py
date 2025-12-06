"""
Firebase integration service for Health & Fitness XAI System
Handles authentication and database operations with Firebase
"""
import firebase_admin
from firebase_admin import credentials, auth, db
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

class FirebaseService:
    """Firebase service for authentication and database operations"""
    
    def __init__(self, credentials_path='firebase_credentials.json'):
        """
        Initialize Firebase service
        
        Args:
            credentials_path: Path to Firebase service account credentials JSON file
        """
        self.credentials_path = credentials_path
        self.app = None
        self.initialized = False
        
        # Try to initialize Firebase if credentials exist
        if os.path.exists(credentials_path):
            try:
                self._initialize_firebase()
            except Exception as e:
                print(f"Firebase initialization warning: {e}")
                print("Falling back to local database mode")
    
    @staticmethod
    def _encode_key(key):
        """
        Encode a key for Firebase (replace invalid characters)
        Firebase doesn't allow @ . # $ [ ] characters in keys
        """
        if not key:
            return key
        # Replace @ with _ and . with - to make email-based keys valid
        return str(key).replace('@', '_').replace('.', '-')
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Load credentials
            cred = credentials.Certificate(self.credentials_path)
            
            # Get database URL from environment variables
            database_url = os.getenv('FIREBASE_DATABASE_URL')
            
            if not database_url:
                print("Firebase initialization error: FIREBASE_DATABASE_URL not set in .env")
                self.initialized = False
                return
            
            # Initialize Firebase app
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
            self.initialized = True
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.initialized = False
    
    def is_initialized(self):
        """Check if Firebase is initialized"""
        return self.initialized
    
    # Authentication Methods
    def register_user(self, email, password, name):
        """
        Register a new user with Firebase Authentication
        
        Args:
            email: User email
            password: User password
            name: User full name
            
        Returns:
            tuple: (success, message, uid)
        """
        if not self.initialized:
            return False, "Firebase not initialized", None
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            
            # Store user metadata in Realtime Database using encoded email as key
            user_data = {
                'email': email,
                'name': name,
                'created_at': datetime.now().isoformat(),
                'profile': None,
                'uid': user.uid
            }
            
            encoded_email = self._encode_key(email)
            db.reference(f'users/{encoded_email}').set(user_data)
            
            return True, "Registration successful", user.uid
        
        except auth.EmailAlreadyExistsError:
            return False, "Email already registered", None
        except auth.InvalidPasswordError:
            return False, "Password must be at least 6 characters", None
        except Exception as e:
            return False, f"Registration error: {str(e)}", None
    
    def authenticate_user(self, email, password):
        """
        Authenticate user by verifying email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            tuple: (success, message, uid)
        """
        if not self.initialized:
            return False, "Firebase not initialized", None
        
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
            
            # Verify password by attempting to sign in with Firebase REST API
            # This is the proper way to verify password on the backend
            import requests
            api_key = os.getenv('FIREBASE_API_KEY')
            
            if not api_key:
                return False, "Firebase API key not configured", None
            
            # Use Firebase REST API to verify password
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                # Password is correct
                return True, "Login successful", user.uid
            else:
                # Password is incorrect
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Invalid password')
                if 'INVALID_PASSWORD' in error_message or 'INVALID_LOGIN_CREDENTIALS' in error_message:
                    return False, "Invalid password", None
                else:
                    return False, error_message, None
        
        except auth.UserNotFoundError:
            return False, "Email not found", None
        except Exception as e:
            return False, f"Authentication error: {str(e)}", None
    
    def get_user(self, uid_or_email):
        """
        Get user data from Firebase
        
        Args:
            uid_or_email: User ID or email (email is preferred)
            
        Returns:
            dict: User data or None
        """
        if not self.initialized:
            return None
        
        try:
            # Encode the key to make it Firebase-safe
            key = self._encode_key(uid_or_email)
            user_data = db.reference(f'users/{key}').get()
            return user_data
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            dict: User data or None
        """
        if not self.initialized:
            return None
        
        try:
            user = auth.get_user_by_email(email)
            return self.get_user(user.uid)
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    # Profile Management
    def update_user_data(self, uid_or_email, user_data):
        """
        Update complete user data (name, email, etc.)
        
        Args:
            uid_or_email: User ID or email (email is preferred for consistency)
            user_data: User data dictionary
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            user_data['updated_at'] = datetime.now().isoformat()
            # Encode the key to make it Firebase-safe
            key = self._encode_key(uid_or_email)
            db.reference(f'users/{key}').update(user_data)
            print(f"[DEBUG] Firebase user data updated for key: {key}")
            return True
        except Exception as e:
            print(f"Error updating user data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_user_profile(self, uid_or_email, profile_data):
        """
        Update user's health profile
        
        Args:
            uid_or_email: User ID or email (email is preferred for consistency)
            profile_data: Health profile data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            profile_data['updated_at'] = datetime.now().isoformat()
            # Encode the key to make it Firebase-safe
            key = self._encode_key(uid_or_email)
            db.reference(f'users/{key}/profile').set(profile_data)
            print(f"[DEBUG] Firebase profile updated for key: {key}")
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_profile(self, uid_or_email):
        """
        Get user's health profile
        
        Args:
            uid_or_email: User ID or email (email is preferred for consistency)
            
        Returns:
            dict: Profile data or None
        """
        if not self.initialized:
            return None
        
        try:
            key = self._encode_key(uid_or_email)
            profile = db.reference(f'users/{key}/profile').get()
            return profile
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    # Feedback Management
    def store_feedback(self, uid_or_email, user_email, feedback_type, advice_text, detailed_comment=None):
        """
        Store user feedback on AI advice
        
        Args:
            uid_or_email: User ID or email (email is preferred)
            user_email: User email
            feedback_type: Type of feedback (helpful, not-helpful, neutral)
            advice_text: The advice being rated
            detailed_comment: Optional detailed comment
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            feedback_entry = {
                'user_email': user_email,
                'feedback_type': feedback_type,
                'advice_text': advice_text[:200],
                'detailed_comment': detailed_comment,
                'timestamp': datetime.now().isoformat()
            }
            
            # Encode the key to make it Firebase-safe
            key = self._encode_key(uid_or_email)
            # Store feedback with auto-generated ID
            feedback_ref = db.reference(f'users/{key}/feedback').push(feedback_entry)
            return True
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def get_user_feedback(self, uid):
        """
        Get all feedback from a specific user
        
        Args:
            uid: User ID
            
        Returns:
            list: User feedback entries
        """
        if not self.initialized:
            return []
        
        try:
            feedback = db.reference(f'users/{uid}/feedback').get()
            if feedback is None:
                return []
            
            # Convert dict to list if needed
            if isinstance(feedback, dict):
                return list(feedback.values())
            return feedback
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []
    
    def get_feedback_stats(self):
        """
        Get feedback statistics across all users
        
        Returns:
            dict: Feedback statistics
        """
        if not self.initialized:
            return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
        
        try:
            all_feedback = db.reference('users').get()
            
            if not all_feedback:
                return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
            
            stats = {
                'total': 0,
                'helpful': 0,
                'not_helpful': 0,
                'neutral': 0
            }
            
            # Iterate through all users and their feedback
            for uid, user_data in all_feedback.items():
                if user_data and 'feedback' in user_data:
                    for feedback_id, feedback in user_data['feedback'].items():
                        stats['total'] += 1
                        feedback_type = feedback.get('feedback_type', 'neutral')
                        if feedback_type == 'helpful':
                            stats['helpful'] += 1
                        elif feedback_type == 'not-helpful':
                            stats['not_helpful'] += 1
                        else:
                            stats['neutral'] += 1
            
            return stats
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
    
    # Tracking Data
    def store_tracking_data(self, uid_or_email, tracking_data):
        """
        Store daily tracking data
        
        Args:
            uid_or_email: User ID or email (email is preferred)
            tracking_data: Daily tracking data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            tracking_data['timestamp'] = datetime.now().isoformat()
            key = self._encode_key(uid_or_email)
            db.reference(f'users/{key}/tracking').push(tracking_data)
            return True
        except Exception as e:
            print(f"Error storing tracking data: {e}")
            return False
    
    def get_user_tracking_data(self, uid):
        """
        Get user's tracking data
        
        Args:
            uid: User ID
            
        Returns:
            list: Tracking data entries
        """
        if not self.initialized:
            return []
        
        try:
            tracking = db.reference(f'users/{uid}/tracking').get()
            if tracking is None:
                return []
            
            if isinstance(tracking, dict):
                return list(tracking.values())
            return tracking
        except Exception as e:
            print(f"Error getting tracking data: {e}")
            return []
    
    # Recommendations
    def store_recommendations(self, uid, recommendations):
        """
        Store AI recommendations
        
        Args:
            uid: User ID
            recommendations: Recommendations data
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            recommendations['timestamp'] = datetime.now().isoformat()
            db.reference(f'users/{uid}/recommendations').push(recommendations)
            return True
        except Exception as e:
            print(f"Error storing recommendations: {e}")
            return False
    
    def get_user_recommendations(self, uid):
        """
        Get user's recommendations
        
        Args:
            uid: User ID
            
        Returns:
            list: Recommendations
        """
        if not self.initialized:
            return []
        
        try:
            recommendations = db.reference(f'users/{uid}/recommendations').get()
            if recommendations is None:
                return []
            
            if isinstance(recommendations, dict):
                return list(recommendations.values())
            return recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []


# Global Firebase service instance
firebase_service = None

def init_firebase(credentials_path='firebase_credentials.json'):
    """Initialize global Firebase service"""
    global firebase_service
    firebase_service = FirebaseService(credentials_path)
    return firebase_service

def get_firebase_service():
    """Get global Firebase service instance"""
    global firebase_service
    if firebase_service is None:
        firebase_service = FirebaseService()
    return firebase_service
