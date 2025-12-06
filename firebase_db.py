"""
Firebase Firestore database module for user authentication and profiles
Stores user data in Firebase Firestore instead of local JSON
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import hashlib
import os
import json


class FirebaseDatabase:
    """Firebase Firestore-based user database"""
    
    def __init__(self, credentials_path='firebase_credentials.json'):
        """Initialize Firebase connection"""
        self.db = None
        self.credentials_path = credentials_path
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Load credentials
                if os.path.exists(self.credentials_path):
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    print("✓ Firebase initialized successfully")
                else:
                    print(f"✗ Firebase credentials not found at {self.credentials_path}")
                    self.db = None
            else:
                self.db = firestore.client()
        except Exception as e:
            print(f"✗ Firebase initialization error: {e}")
            self.db = None
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, name):
        """Register a new user in Firebase"""
        if not self.db:
            return False, "Firebase not initialized"
        
        try:
            # Check if user already exists
            user_doc = self.db.collection('users').document(email).get()
            if user_doc.exists:
                return False, "Email already registered"
            
            # Create new user
            self.db.collection('users').document(email).set({
                'email': email,
                'password': self._hash_password(password),
                'name': name,
                'created_at': datetime.now().isoformat(),
                'profile': None,
                'updated_at': datetime.now().isoformat()
            })
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        if not self.db:
            return False, "Firebase not initialized"
        
        try:
            user_doc = self.db.collection('users').document(email).get()
            if not user_doc.exists:
                return False, "Email not found"
            
            user_data = user_doc.to_dict()
            if user_data['password'] != self._hash_password(password):
                return False, "Invalid password"
            
            return True, "Login successful"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def get_user(self, email):
        """Get user data from Firebase"""
        if not self.db:
            return None
        
        try:
            user_doc = self.db.collection('users').document(email).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_profile(self, email, profile_data):
        """Update user's health profile in Firebase"""
        if not self.db:
            return False
        
        try:
            self.db.collection('users').document(email).update({
                'profile': profile_data,
                'updated_at': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def get_user_profile(self, email):
        """Get user's health profile from Firebase"""
        if not self.db:
            return None
        
        try:
            user_doc = self.db.collection('users').document(email).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return user_data.get('profile')
            return None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def get_all_users(self):
        """Get all users from Firebase (admin only)"""
        if not self.db:
            return {}
        
        try:
            users = {}
            docs = self.db.collection('users').stream()
            for doc in docs:
                users[doc.id] = doc.to_dict()
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return {}
    
    def is_admin(self, email):
        """Check if user is admin"""
        return email == 'admin@123.com'
    
    def store_feedback(self, user_email, feedback_type, advice_text, detailed_comment=None):
        """Store user feedback in Firebase"""
        if not self.db:
            return False
        
        try:
            feedback_entry = {
                'user_email': user_email,
                'feedback_type': feedback_type,
                'advice_text': advice_text[:200],  # Store first 200 chars
                'detailed_comment': detailed_comment,
                'timestamp': datetime.now().isoformat()
            }
            self.db.collection('feedback').add(feedback_entry)
            return True
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def get_feedback_stats(self):
        """Get feedback statistics from Firebase"""
        if not self.db:
            return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
        
        try:
            docs = self.db.collection('feedback').stream()
            feedback_list = [doc.to_dict() for doc in docs]
            
            stats = {
                'total': len(feedback_list),
                'helpful': sum(1 for f in feedback_list if f['feedback_type'] == 'helpful'),
                'not_helpful': sum(1 for f in feedback_list if f['feedback_type'] == 'not-helpful'),
                'neutral': sum(1 for f in feedback_list if f['feedback_type'] == 'neutral')
            }
            return stats
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
    
    def get_user_feedback(self, user_email):
        """Get all feedback from a specific user"""
        if not self.db:
            return []
        
        try:
            docs = self.db.collection('feedback').where('user_email', '==', user_email).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error getting user feedback: {e}")
            return []
    
    def migrate_from_json(self, json_file='users_db.json'):
        """Migrate user data from JSON file to Firebase"""
        if not self.db:
            return False, "Firebase not initialized"
        
        try:
            if not os.path.exists(json_file):
                return False, f"JSON file not found: {json_file}"
            
            with open(json_file, 'r') as f:
                users_data = json.load(f)
            
            migrated_count = 0
            for email, user_info in users_data.items():
                try:
                    self.db.collection('users').document(email).set({
                        'email': email,
                        'password': user_info.get('password'),
                        'name': user_info.get('name'),
                        'created_at': user_info.get('created_at'),
                        'profile': user_info.get('profile'),
                        'updated_at': datetime.now().isoformat()
                    })
                    migrated_count += 1
                except Exception as e:
                    print(f"Error migrating user {email}: {e}")
            
            return True, f"Successfully migrated {migrated_count} users to Firebase"
        except Exception as e:
            return False, f"Migration error: {str(e)}"
