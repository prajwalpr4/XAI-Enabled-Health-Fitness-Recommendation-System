"""
Simple database module for user authentication
"""
import json
import os
from datetime import datetime
import hashlib


class UserDatabase:
    """Simple JSON-based user database"""
    
    def __init__(self, db_file='users_db.json', feedback_file='feedback_db.json'):
        self.db_file = db_file
        self.feedback_file = feedback_file
        self.users = self._load_database()
        self.feedback = self._load_feedback()
    
    def _load_database(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_database(self):
        """Save users to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, name):
        """Register a new user"""
        if email in self.users:
            return False, "Email already registered"
        
        self.users[email] = {
            'password': self._hash_password(password),
            'name': name,
            'created_at': datetime.now().isoformat(),
            'profile': None
        }
        self._save_database()
        return True, "Registration successful"
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        if email not in self.users:
            return False, "Email not found"
        
        if self.users[email]['password'] != self._hash_password(password):
            return False, "Invalid password"
        
        return True, "Login successful"
    
    def get_user(self, email):
        """Get user data"""
        return self.users.get(email)
    
    def update_user_profile(self, email, profile_data):
        """Update user's health profile"""
        if email in self.users:
            self.users[email]['profile'] = profile_data
            self._save_database()
            return True
        return False
    
    def get_user_profile(self, email):
        """Get user's health profile"""
        if email in self.users:
            return self.users[email].get('profile')
        return None
    
    def get_all_users(self):
        """Get all users (admin only)"""
        return self.users
    
    def is_admin(self, email):
        """Check if user is admin"""
        return email == 'admin@123.com'
    
    def _load_feedback(self):
        """Load feedback from JSON file"""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_feedback(self):
        """Save feedback to JSON file"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback, f, indent=2)
    
    def store_feedback(self, user_email, feedback_type, advice_text, detailed_comment=None):
        """Store user feedback on AI advice"""
        feedback_entry = {
            'user_email': user_email,
            'feedback_type': feedback_type,
            'advice_text': advice_text[:200],  # Store first 200 chars of advice
            'detailed_comment': detailed_comment,
            'timestamp': datetime.now().isoformat()
        }
        self.feedback.append(feedback_entry)
        self._save_feedback()
        return True
    
    def get_feedback_stats(self):
        """Get feedback statistics"""
        if not self.feedback:
            return {'total': 0, 'helpful': 0, 'not_helpful': 0, 'neutral': 0}
        
        stats = {
            'total': len(self.feedback),
            'helpful': sum(1 for f in self.feedback if f['feedback_type'] == 'helpful'),
            'not_helpful': sum(1 for f in self.feedback if f['feedback_type'] == 'not-helpful'),
            'neutral': sum(1 for f in self.feedback if f['feedback_type'] == 'neutral')
        }
        return stats
    
    def get_user_feedback(self, user_email):
        """Get all feedback from a specific user"""
        return [f for f in self.feedback if f['user_email'] == user_email]
