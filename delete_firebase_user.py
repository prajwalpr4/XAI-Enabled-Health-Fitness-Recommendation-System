#!/usr/bin/env python3
"""
Delete Firebase User Script
Allows you to delete a user from Firebase Authentication and Database
"""

import firebase_admin
from firebase_admin import credentials, auth, db
import os
from dotenv import load_dotenv

load_dotenv()

def delete_user_by_email(email):
    """Delete a user by email from Firebase"""
    
    try:
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred = credentials.Certificate('firebase_credentials.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
            })
        
        print(f"\n{'='*70}")
        print(f"  DELETING USER: {email}")
        print(f"{'='*70}\n")
        
        # Step 1: Get user by email
        print(f"1. Finding user by email: {email}")
        try:
            user = auth.get_user_by_email(email)
            uid = user.uid
            print(f"   ✓ Found user with UID: {uid}")
        except auth.UserNotFoundError:
            print(f"   ✗ User not found in Firebase Authentication")
            return False
        
        # Step 2: Delete from Authentication
        print(f"\n2. Deleting from Firebase Authentication...")
        try:
            auth.delete_user(uid)
            print(f"   ✓ User deleted from Authentication")
        except Exception as e:
            print(f"   ✗ Error deleting from Authentication: {e}")
            return False
        
        # Step 3: Delete from Database
        print(f"\n3. Deleting from Firebase Database...")
        try:
            db.reference(f'users/{uid}').delete()
            print(f"   ✓ User data deleted from Database")
        except Exception as e:
            print(f"   ✗ Error deleting from Database: {e}")
            return False
        
        print(f"\n{'='*70}")
        print(f"  ✓ USER DELETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        print(f"You can now register with email: {email}\n")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        return False


def list_all_users():
    """List all users in Firebase Authentication"""
    
    try:
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred = credentials.Certificate('firebase_credentials.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
            })
        
        print(f"\n{'='*70}")
        print(f"  ALL FIREBASE USERS")
        print(f"{'='*70}\n")
        
        # Get all users
        page = auth.list_users()
        
        if not page.users:
            print("No users found in Firebase Authentication\n")
            return
        
        print(f"Total users: {len(page.users)}\n")
        print(f"{'Email':<40} {'UID':<30}")
        print(f"{'-'*40} {'-'*30}")
        
        for user in page.users:
            email = user.email if user.email else "No email"
            print(f"{email:<40} {user.uid:<30}")
        
        print(f"\n{'='*70}\n")
    
    except Exception as e:
        print(f"\n✗ Error: {e}\n")


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("  FIREBASE USER MANAGEMENT")
    print("="*70 + "\n")
    
    print("Options:")
    print("1. Delete user by email")
    print("2. List all users")
    print("3. Exit\n")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        email = input("\nEnter email to delete: ").strip()
        if email:
            delete_user_by_email(email)
        else:
            print("Invalid email")
    
    elif choice == "2":
        list_all_users()
    
    elif choice == "3":
        print("Exiting...\n")
    
    else:
        print("Invalid option\n")


if __name__ == '__main__':
    main()
