"""
Script to create an admin user in Firebase Authentication
"""
import os
import sys
import firebase_admin
from firebase_admin import auth, credentials
from firebase_service import FirebaseService
from database import UserDatabase
import hashlib

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate('firebase_credentials.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': f"https://{cred.project_id}.firebaseio.com"
            })
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {str(e)}")
        return False

def create_admin_user(email, password, name="Admin User"):
    """Create an admin user in Firebase Authentication and local database"""
    try:
        # Initialize Firebase Admin SDK
        if not initialize_firebase():
            return False
        
        # Initialize database
        db = UserDatabase()
        
        # Check if user already exists in Firebase
        try:
            user = auth.get_user_by_email(email)
            print(f"✅ User {email} already exists in Firebase Authentication")
            # Update the user to ensure the password is set correctly
            auth.update_user(user.uid, password=password)
            print(f"✅ Updated password for admin user: {email}")
        except auth.UserNotFoundError:
            # Create new user in Firebase
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=True
            )
            print(f"✅ Created new admin user: {email}")
        
        # Set custom claims for admin access in Firebase
        auth.set_custom_user_claims(user.uid, {'admin': True})
        print(f"✅ Set admin privileges for user: {email}")
        
        # Check if user exists in local database
        if email not in db.users:
            # Register new user in local database
            success, message = db.register_user(email, password, name)
            if success:
                print(f"✅ Added admin user to local database: {email}")
                # Update user to be admin in local database
                db.users[email]['is_admin'] = True
                db._save_database()
                print(f"✅ Set admin flag in local database for: {email}")
            else:
                print(f"⚠️ Could not add user to local database: {message}")
        else:
            # Update existing user in local database
            db.users[email]['is_admin'] = True
            # Update password hash if needed
            db.users[email]['password'] = hashlib.sha256(password.encode()).hexdigest()
            db._save_database()
            print(f"✅ Updated admin privileges in local database for: {email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Default admin credentials
    ADMIN_EMAIL = "admin@123.com"
    ADMIN_PASSWORD = "admin123"
    
    print(f"Setting up admin user: {ADMIN_EMAIL}")
    if create_admin_user(ADMIN_EMAIL, ADMIN_PASSWORD):
        print("\n✅ Admin setup completed successfully!")
        print(f"Email: {ADMIN_EMAIL}")
        print("Password: ********")
        print("\nYou can now log in to the admin panel at /admin")
        print("\nIMPORTANT: Make sure the Firebase Authentication email/password provider is enabled:")
        print("1. Go to Firebase Console")
        print("2. Select your project")
        print("3. Go to Authentication > Sign-in method")
        print("4. Enable Email/Password provider if not already enabled")
    else:
        print("\n❌ Failed to set up admin user. Please check the error messages above.")
        sys.exit(1)
