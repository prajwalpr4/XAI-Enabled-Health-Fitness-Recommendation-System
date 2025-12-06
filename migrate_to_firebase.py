"""
Migration script to move user data from JSON to Firebase Firestore
Run this script to migrate all existing user data to Firebase
"""
import sys
from firebase_db import FirebaseDatabase
import json
import os


def main():
    """Main migration function"""
    print("=" * 60)
    print("User Data Migration: JSON → Firebase Firestore")
    print("=" * 60)
    
    # Initialize Firebase
    print("\n1. Initializing Firebase connection...")
    firebase_db = FirebaseDatabase('firebase_credentials.json')
    
    if not firebase_db.db:
        print("✗ Failed to initialize Firebase")
        print("Please ensure firebase_credentials.json exists in the project root")
        return False
    
    print("✓ Firebase connected successfully")
    
    # Check if JSON file exists
    json_file = 'users_db.json'
    if not os.path.exists(json_file):
        print(f"\n✗ JSON file not found: {json_file}")
        return False
    
    # Load and display JSON data
    print(f"\n2. Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        users_data = json.load(f)
    
    print(f"✓ Found {len(users_data)} users to migrate")
    
    # Display users to be migrated
    print("\nUsers to migrate:")
    for email in users_data.keys():
        print(f"  - {email}")
    
    # Confirm migration
    print("\n" + "=" * 60)
    response = input("Proceed with migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Migration cancelled")
        return False
    
    # Perform migration
    print("\n3. Migrating data to Firebase...")
    success, message = firebase_db.migrate_from_json(json_file)
    
    if success:
        print(f"✓ {message}")
        
        # Verify migration
        print("\n4. Verifying migration...")
        all_users = firebase_db.get_all_users()
        print(f"✓ Verified: {len(all_users)} users in Firebase")
        
        # Display sample user
        if all_users:
            first_email = list(all_users.keys())[0]
            print(f"\nSample user data ({first_email}):")
            user_data = all_users[first_email]
            print(f"  Name: {user_data.get('name')}")
            print(f"  Created: {user_data.get('created_at')}")
            if user_data.get('profile'):
                profile = user_data['profile']
                print(f"  Profile: Age={profile.get('age')}, Weight={profile.get('weight')}kg")
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        return True
    else:
        print(f"✗ Migration failed: {message}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
