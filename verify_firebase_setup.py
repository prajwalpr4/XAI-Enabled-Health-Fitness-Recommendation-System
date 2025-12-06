#!/usr/bin/env python3
"""
Firebase Setup Verification Script
Checks if Firebase is properly configured and provides guidance
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseSetupVerifier:
    """Verify Firebase setup and provide guidance"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.success_items = []
    
    def check_credentials_file(self):
        """Check if firebase_credentials.json exists and is valid"""
        cred_path = self.project_root / 'firebase_credentials.json'
        
        if not cred_path.exists():
            self.issues.append(
                "❌ firebase_credentials.json NOT FOUND\n"
                "   Location: " + str(cred_path) + "\n"
                "   Action: Download from Firebase Console and place here"
            )
            return False
        
        try:
            with open(cred_path, 'r') as f:
                cred_data = json.load(f)
            
            # Check for required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [f for f in required_fields if f not in cred_data]
            
            if missing_fields:
                self.issues.append(
                    f"❌ firebase_credentials.json is INVALID\n"
                    f"   Missing fields: {missing_fields}\n"
                    f"   Action: Download a new credentials file from Firebase Console"
                )
                return False
            
            self.success_items.append(
                "✅ firebase_credentials.json found and valid\n"
                f"   Project: {cred_data.get('project_id', 'Unknown')}"
            )
            return True
        
        except json.JSONDecodeError:
            self.issues.append(
                "❌ firebase_credentials.json is NOT valid JSON\n"
                "   Action: Download a new credentials file from Firebase Console"
            )
            return False
        except Exception as e:
            self.issues.append(f"❌ Error reading credentials: {e}")
            return False
    
    def check_env_variables(self):
        """Check if .env has Firebase web configuration"""
        required_vars = [
            'FIREBASE_API_KEY',
            'FIREBASE_AUTH_DOMAIN',
            'FIREBASE_DATABASE_URL_WEB',
            'FIREBASE_PROJECT_ID',
            'FIREBASE_APP_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.warnings.append(
                f"⚠️  Missing environment variables: {missing_vars}\n"
                f"   Location: .env file\n"
                f"   Action: Add these variables to .env"
            )
            return False
        
        self.success_items.append(
            "✅ All Firebase environment variables configured\n"
            f"   Project: {os.getenv('FIREBASE_PROJECT_ID', 'Unknown')}"
        )
        return True
    
    def check_firebase_module(self):
        """Check if firebase_service.py exists"""
        firebase_module = self.project_root / 'firebase_service.py'
        
        if not firebase_module.exists():
            self.issues.append(
                "❌ firebase_service.py NOT FOUND\n"
                f"   Location: {firebase_module}\n"
                f"   Action: This file should exist in the project"
            )
            return False
        
        self.success_items.append("✅ firebase_service.py found")
        return True
    
    def check_firebase_client(self):
        """Check if firebase-client.js exists"""
        client_file = self.project_root / 'static' / 'firebase-client.js'
        
        if not client_file.exists():
            self.warnings.append(
                "⚠️  firebase-client.js NOT FOUND\n"
                f"   Location: {client_file}\n"
                f"   Action: Frontend Firebase integration not available"
            )
            return False
        
        self.success_items.append("✅ firebase-client.js found")
        return True
    
    def check_templates(self):
        """Check if templates are updated"""
        templates_dir = self.project_root / 'templates'
        
        if not templates_dir.exists():
            self.warnings.append(
                "⚠️  templates directory NOT FOUND\n"
                f"   Location: {templates_dir}"
            )
            return False
        
        self.success_items.append("✅ templates directory found")
        return True
    
    def verify_all(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("  FIREBASE SETUP VERIFICATION")
        print("="*70 + "\n")
        
        print("Checking Firebase configuration...\n")
        
        # Run all checks
        cred_ok = self.check_credentials_file()
        env_ok = self.check_env_variables()
        module_ok = self.check_firebase_module()
        client_ok = self.check_firebase_client()
        templates_ok = self.check_templates()
        
        # Print results
        print("✅ SUCCESS ITEMS:")
        print("-" * 70)
        for item in self.success_items:
            print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            print("-" * 70)
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n❌ ISSUES:")
            print("-" * 70)
            for issue in self.issues:
                print(f"  {issue}")
        
        # Overall status
        print("\n" + "="*70)
        if self.issues:
            print("  STATUS: ❌ SETUP INCOMPLETE")
            print("="*70)
            print("\nACTION REQUIRED:")
            print("  1. Download firebase_credentials.json from Firebase Console")
            print("  2. Place it in: " + str(self.project_root))
            print("  3. Restart the application")
            print("\nFor detailed instructions, see: COMPLETE_SETUP_CHECKLIST.md")
            return False
        elif self.warnings:
            print("  STATUS: ⚠️  SETUP PARTIAL")
            print("="*70)
            print("\nRECOMMENDED ACTIONS:")
            for warning in self.warnings:
                print(f"  - {warning.split(chr(10))[0]}")
            return True
        else:
            print("  STATUS: ✅ SETUP COMPLETE")
            print("="*70)
            print("\nFIREBASE IS FULLY CONFIGURED!")
            print("  - Credentials: ✅ Valid")
            print("  - Configuration: ✅ Complete")
            print("  - Frontend: ✅ Ready")
            print("  - Backend: ✅ Ready")
            print("\nYou can now:")
            print("  1. Register users")
            print("  2. Store profiles in Firebase")
            print("  3. Collect feedback")
            print("  4. Track activity")
            print("  5. Store recommendations")
            return True
    
    def print_next_steps(self):
        """Print next steps"""
        if self.issues:
            print("\nNEXT STEPS:")
            print("-" * 70)
            print("1. Go to: https://console.firebase.google.com/")
            print("2. Select project: xai-fitness")
            print("3. Go to: Project Settings → Service Accounts")
            print("4. Click: Generate New Private Key")
            print("5. Save the JSON file")
            print("6. Rename to: firebase_credentials.json")
            print("7. Place in: " + str(self.project_root))
            print("8. Restart the application")
            print("9. Run this script again to verify")


def main():
    """Main function"""
    verifier = FirebaseSetupVerifier()
    success = verifier.verify_all()
    verifier.print_next_steps()
    
    print("\n" + "="*70 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
