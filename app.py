"""
Web Application using Flask
Provides user interface for the Health & Fitness XAI System
Supports both local and Firebase storage
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from main import HealthFitnessXAISystem
from database import UserDatabase
from tracker import DailyTracker
from llm_service import GeminiService
from firebase_service import get_firebase_service
from firebase_web_config import FirebaseWebConfig
from dotenv import load_dotenv
import secrets
import json
from datetime import datetime
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Allow Firebase scripts and other necessary external resources
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://www.gstatic.com "
        "https://www.googleapis.com "
        "https://cdn.firebase.com "
        "https://*.firebaseapp.com "
        "https://*.firebase.google.com "
        "https://identitytoolkit.googleapis.com "
        "https://securetoken.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https:; "
        "connect-src 'self' "
        "https://*.firebaseio.com "
        "https://*.firebase.google.com "
        "https://*.firebaseapp.com "
        "https://www.googleapis.com "
        "https://identitytoolkit.googleapis.com "
        "https://securetoken.googleapis.com "
        "https://www.gstatic.com "
        "wss://*.firebaseio.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https:; "
        "frame-src https://*.firebaseapp.com; "
        "object-src 'none'"
    )
    return response

# Initialize the system and database
system = HealthFitnessXAISystem()
db = UserDatabase()

# Initialize Firebase service (optional - falls back to local storage if not configured)
firebase = get_firebase_service()
use_firebase = firebase.is_initialized()

if use_firebase:
    print("[OK] Firebase initialized - using cloud storage")
else:
    print("[WARNING] Firebase not initialized - using local storage")

# Migrate existing profiles to include calculated metrics
def migrate_profiles():
    """Migrate existing profiles to include BMI, BMR, TDEE calculations"""
    try:
        all_users = db.get_all_users()
        for email, user_data in all_users.items():
            if user_data.get('profile') and user_data['profile'] is not None:
                profile = user_data['profile']
                # Check if profile is missing calculated metrics
                if 'bmi' not in profile or profile.get('bmi') is None:
                    # Recreate the profile with calculations
                    try:
                        from models.user_profile import UserProfile
                        user_profile = UserProfile.from_dict(profile)
                        # Save the updated profile with calculated metrics
                        db.update_user_profile(email, user_profile.to_dict())
                        print(f"[OK] Migrated profile for {email}")
                    except Exception as e:
                        print(f"[ERROR] Error migrating profile for {email}: {e}")
    except Exception as e:
        print(f"Migration error: {e}")

# Run migration on startup
migrate_profiles()


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    from flask import send_from_directory
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/api/firebase-config', methods=['GET'])
def get_firebase_config():
    """Serve Firebase web configuration to client"""
    try:
        config = FirebaseWebConfig.get_config()
        is_valid, missing = FirebaseWebConfig.validate_config()
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'Missing Firebase configuration: {missing}'
            }), 400
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_name = session.get('user_name', 'User')
    
    # Check if user has existing profile and should see recommendations
    user_id = session.get('user_id')
    show_recommendations = False
    plan = None
    
    if user_id:
        try:
            # User has profile, generate and show recommendations automatically
            plan = system.generate_complete_plan(user_id)
            
            # Get user profile for Gemini
            user_email = session.get('user_email')
            user_profile = db.get_user_profile(user_email)
            if user_profile:
                try:
                    # Initialize Gemini service
                    gemini = GeminiService()
                    
                    # Create context for Gemini
                    context = f"""
                    Current Plan Summary:
                    - Goal: {plan.get('goal', 'Not specified')}
                    - Daily Calories: {plan.get('daily_calories', 'Not calculated')}
                    - Workout Frequency: {plan.get('workout_frequency', 'Not specified')}
                    - Dietary Focus: {plan.get('dietary_focus', 'Balanced')}
                    """
                    
                    # Get AI-powered advice
                    ai_advice = gemini.get_personalized_advice(
                        user_profile=user_profile,
                        context=context
                    )
                    
                    # Add AI advice to the plan
                    plan['ai_advice'] = ai_advice
                    
                except Exception as e:
                    print(f"Warning: Could not generate AI advice: {e}")
                    plan['ai_advice'] = "AI-powered advice is currently unavailable. Please try again later."
            else:
                plan['ai_advice'] = "Please complete your profile to get personalized AI advice."
            
            show_recommendations = True
        except Exception as e:
            print(f"Error generating plan: {e}")
            # If plan generation fails, show profile form
            show_recommendations = False
    
    return render_template('index.html', user_name=user_name, show_recommendations=show_recommendations, plan=plan)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - supports both Firebase and local authentication"""
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Check for admin credentials
        if email == 'admin@123.com' and password == 'admin123':
            session['user_email'] = email
            session['user_name'] = 'Admin'
            session['is_admin'] = True
            return jsonify({'success': True, 'message': 'Admin login successful', 'is_admin': True})
        
        # Try local database first (most reliable)
        success, message = db.authenticate_user(email, password)
        
        if success:
            # User authenticated in local database
            user = db.get_user(email)
            session['user_email'] = email
            session['user_name'] = user['name'] if user else 'User'
            session['is_admin'] = False
            
            # Sync user data to Firebase if available
            if use_firebase:
                try:
                    user_data_to_sync = {
                        'email': email,
                        'name': user.get('name', 'User') if user else 'User',
                        'created_at': user.get('created_at') if user else datetime.now().isoformat()
                    }
                    firebase.update_user_data(email, user_data_to_sync)
                except Exception as e:
                    print(f"Warning: Could not sync user data to Firebase: {e}")
            
            # Load existing profile if available
            profile = db.get_user_profile(email)
            has_profile = False
            if profile:
                session['user_id'] = profile['user_id']
                # Recreate user in system
                system.create_user(profile)
                has_profile = True
                
                # Sync profile to Firebase
                if use_firebase:
                    try:
                        firebase.update_user_profile(email, profile)
                    except Exception as e:
                        print(f"Warning: Could not sync profile to Firebase: {e}")
            
            return jsonify({'success': True, 'message': message, 'is_admin': False, 'has_profile': has_profile, 'storage': 'local'})
        else:
            # If local auth fails, try Firebase
            if use_firebase:
                success, message, uid = firebase.authenticate_user(email, password)
                if success:
                    user = firebase.get_user(uid)
                    session['user_email'] = email
                    session['user_name'] = user.get('name', 'User') if user else 'User'
                    session['user_uid'] = uid
                    session['is_admin'] = False
                    
                    # Load existing profile if available
                    profile = firebase.get_user_profile(uid)
                    has_profile = False
                    if profile:
                        session['user_id'] = profile.get('user_id')
                        # Recreate user in system
                        system.create_user(profile)
                        has_profile = True
                    
                    return jsonify({'success': True, 'message': message, 'is_admin': False, 'has_profile': has_profile, 'storage': 'firebase'})
                else:
                    return jsonify({'success': False, 'error': message}), 401
            else:
                # No Firebase and local auth failed
                return jsonify({'success': False, 'error': message}), 401
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page - supports both Firebase and local storage"""
    if request.method == 'GET':
        # Add cache-busting headers for GET requests
        response = make_response(render_template('signup.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Validate input
        if not email or not password or not name:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Try Firebase first if available
        if use_firebase:
            success, message, uid = firebase.register_user(email, password, name)
            if success:
                return jsonify({'success': True, 'message': 'Account created successfully!', 'storage': 'firebase'})
            else:
                # If Firebase registration fails, provide helpful error message
                if 'already exists' in message.lower() or 'email already' in message.lower():
                    return jsonify({'success': False, 'error': 'This email is already registered. Please login or use a different email.'}), 400
                else:
                    return jsonify({'success': False, 'error': message}), 400
        else:
            # Fall back to local database
            success, message = db.register_user(email, password, name)
            
            if success:
                # Also sync to Firebase if available
                if use_firebase:
                    try:
                        user_data = {
                            'email': email,
                            'name': name,
                            'created_at': datetime.now().isoformat()
                        }
                        firebase.update_user_data(email, user_data)
                    except Exception as e:
                        print(f"Warning: Could not sync user data to Firebase: {e}")
                
                return jsonify({'success': True, 'message': 'Account created successfully!', 'storage': 'local'})
            else:
                # If local registration fails, provide helpful error message
                if 'already exists' in message.lower() or 'email already' in message.lower():
                    return jsonify({'success': False, 'error': 'This email is already registered. Please login or use a different email.'}), 400
                else:
                    return jsonify({'success': False, 'error': message}), 400
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin
    if not db.is_admin(session['user_email']):
        return "Access Denied: Admin Only", 403
    
    # Get all users
    all_users = db.get_all_users()
    
    return render_template('admin.html', users=all_users)


@app.route('/admin/user/<email>')
def admin_user_detail(email):
    """View specific user details (admin only)"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if not db.is_admin(session['user_email']):
        return "Access Denied: Admin Only", 403
    
    user = db.get_user(email)
    if not user:
        return "User not found", 404
    
    return render_template('admin_user_detail.html', user_email=email, user=user)


@app.route('/admin/delete-user', methods=['POST'])
def delete_user():
    """Delete a user (admin only)"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if not db.is_admin(session['user_email']):
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        email_to_delete = data.get('email')
        
        if not email_to_delete:
            return jsonify({'success': False, 'error': 'Email not provided'}), 400
        
        # Prevent deleting admin account
        if db.is_admin(email_to_delete):
            return jsonify({'success': False, 'error': 'Cannot delete admin account'}), 403
        
        # Delete user from database
        if email_to_delete in db.users:
            del db.users[email_to_delete]
            db._save_database()
            
            # Also try to delete from Firebase if available
            try:
                firebase_service = get_firebase_service()
                if firebase_service and firebase_service.initialized:
                    user = firebase_service.auth.get_user_by_email(email_to_delete)
                    firebase_service.auth.delete_user(user.uid)
            except Exception as e:
                # Log the error but don't fail the deletion
                print(f"Warning: Could not delete user from Firebase: {str(e)}")
            
            return jsonify({'success': True, 'message': f'User {email_to_delete} deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/profile')
def user_profile():
    """User profile page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # Admins can't access user profile
    if db.is_admin(session['user_email']):
        return redirect(url_for('admin_dashboard'))
    
    email = session['user_email']
    user_name = session.get('user_name', 'User')
    
    # Try to get user from local database first
    user = db.get_user(email)
    
    if user:
        # User found in local database
        profile = user.get('profile')
        
        # If no profile in local DB, try Firebase
        if not profile and use_firebase:
            firebase_profile = firebase.get_user_profile(email)
            if firebase_profile:
                # Sync Firebase profile to local database
                user['profile'] = firebase_profile
                db.update_user_profile(email, firebase_profile)
                profile = firebase_profile
                print(f"[DEBUG] Profile page - Synced profile from Firebase for {email}")
        
        print(f"[DEBUG] Profile page - User {email} loaded from local DB, profile: {profile}")
    else:
        # If not in local database, try Firebase
        if use_firebase and 'user_uid' in session:
            uid = session['user_uid']
            firebase_user = firebase.get_user(uid)
            if firebase_user:
                # Create a user dict from Firebase data
                profile = firebase.get_user_profile(email)
                user = {
                    'name': firebase_user.get('name', user_name),
                    'email': email,
                    'created_at': firebase_user.get('created_at', ''),
                    'profile': profile
                }
                print(f"[DEBUG] Profile page - User {email} loaded from Firebase, profile: {profile}")
        
        # If still no user, create a minimal user object from session
        if not user:
            user = {
                'name': user_name,
                'email': email,
                'created_at': '',
                'profile': None
            }
            print(f"[DEBUG] Profile page - User {email} created from session, no profile")
    
    return render_template('profile.html', user=user, user_email=email)


@app.route('/tracker')
def tracker():
    """Daily tracker page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    return render_template('tracker.html')


@app.route('/dashboard')
def dashboard():
    """Modern dashboard page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')


@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    """Get current user information"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    email = session['user_email']
    user_name = session.get('user_name', 'User')
    
    # Try to get user from local database first
    user = db.get_user(email)
    if user:
        profile = user.get('profile', {})
        return jsonify({
            'success': True,
            'name': user.get('name', user_name),
            'email': email,
            'sleep_hours': profile.get('sleep_hours', 7.0)
        })
    
    # If not in local database, try Firebase
    if use_firebase and 'user_uid' in session:
        uid = session['user_uid']
        firebase_user = firebase.get_user(uid)
        if firebase_user:
            profile = firebase.get_user_profile(uid)
            return jsonify({
                'success': True,
                'name': firebase_user.get('name', user_name),
                'email': email,
                'sleep_hours': profile.get('sleep_hours', 7.0) if profile else 7.0
            })
    
    # If user not found in either database, return session data
    return jsonify({
        'success': True,
        'name': user_name,
        'email': email,
        'sleep_hours': 7.0
    })


@app.route('/create_profile', methods=['POST'])
def create_profile():
    """Create user profile - supports both Firebase and local storage"""
    try:
        data = request.json
        
        # Check if user is logged in
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        # Generate unique user ID or use existing
        if 'user_id' in session:
            user_id = session['user_id']
            data['user_id'] = user_id
        else:
            user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            data['user_id'] = user_id
            session['user_id'] = user_id
        
        # Create user
        user = system.create_user(data)
        user_dict = user.to_dict()
        
        # Save profile to database
        email = session['user_email']
        
        # Save to local database first
        db.update_user_profile(email, user_dict)
        
        # Also save to Firebase if available
        if use_firebase:
            try:
                firebase.update_user_profile(email, user_dict)
                print(f"[DEBUG] Profile synced to Firebase for {email}")
            except Exception as e:
                print(f"Warning: Could not sync profile to Firebase: {e}")
        
        return jsonify({
            'success': True,
            'user': user_dict,
            'message': 'Profile created successfully!'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations with Gemini AI enhancement"""
    try:
        # Check if user is logged in
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No user profile found. Please create a profile first.'
            }), 400
        
        # Generate complete plan
        plan = system.generate_complete_plan(user_id)
        
        # Get user profile for Gemini
        user_email = session.get('user_email')
        user_profile = db.get_user_profile(user_email)
        if user_profile:
            try:
                # Initialize Gemini service
                gemini = GeminiService()
                
                # Create context for Gemini
                context = f"""
                Current Plan Summary:
                - Goal: {plan.get('goal', 'Not specified')}
                - Daily Calories: {plan.get('daily_calories', 'Not calculated')}
                - Workout Frequency: {plan.get('workout_frequency', 'Not specified')}
                - Dietary Focus: {plan.get('dietary_focus', 'Balanced')}
                """
                
                # Get AI-powered advice
                ai_advice = gemini.get_personalized_advice(
                    user_profile=user_profile,
                    context=context
                )
                
                # Add AI advice to the plan
                plan['ai_advice'] = ai_advice
                
            except Exception as e:
                print(f"Warning: Could not generate AI advice: {e}")
                plan['ai_advice'] = "AI-powered advice is currently unavailable. Please try again later."
        else:
            plan['ai_advice'] = "Please complete your profile to get personalized AI advice."
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    try:
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No user profile found.'
            }), 400
        
        updates = request.json
        user = system.update_user(user_id, updates)
        
        # Update in local database
        profile_dict = user.to_dict()
        db.update_user_profile(session['user_email'], profile_dict)

        # Also update in Firebase if enabled
        if use_firebase:
            try:
                email = session.get('user_email')
                print(f"[DEBUG] Updating Firebase profile - Email: {email}")
                print(f"[DEBUG] Profile data: {profile_dict}")
                
                if email:
                    result = firebase.update_user_profile(email, profile_dict)
                    print(f"[DEBUG] Firebase update result: {result}")
                else:
                    print(f"[DEBUG] No email found in session. Session keys: {list(session.keys())}")
            except Exception as firebase_error:
                # Log but do not fail the request if Firebase sync has issues
                print(f"Firebase profile sync error: {firebase_error}")
                import traceback
                traceback.print_exc()
        
        return jsonify({
            'success': True,
            'user': profile_dict,
            'message': 'Profile updated successfully!'
        })
    
    except Exception as e:
        print(f"[ERROR] /update_profile error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/export_plan', methods=['GET'])
def export_plan():
    """Export plan to JSON"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No user profile found.'
            }), 400
        
        plan_json = system.export_plan(user_id)
        
        return jsonify({
            'success': True,
            'plan_json': plan_json
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/tracking_template', methods=['GET'])
def tracking_template():
    """Get progress tracking template"""
    template = system.get_progress_tracking_template()
    return jsonify({
        'success': True,
        'template': template
    })


@app.route('/tracker/today', methods=['GET'])
def get_today_tracker():
    """Get today's tracker data"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    tracker = DailyTracker(session['user_email'])
    today_data = tracker.get_today_data()
    stats = tracker.get_progress_stats()
    
    return jsonify({
        'success': True,
        'data': today_data,
        'stats': stats
    })


@app.route('/tracker/steps', methods=['POST'])
def update_steps():
    """Update step count"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    steps = data.get('steps', 0)
    email = session['user_email']
    
    tracker = DailyTracker(email)
    result = tracker.update_steps(steps)
    
    # Also save to Firebase if enabled
    if use_firebase:
        try:
            tracking_data = {
                'steps': steps,
                'date': datetime.now().isoformat(),
                'type': 'steps_update'
            }
            firebase.store_tracking_data(email, tracking_data)
        except Exception as e:
            print(f"Firebase tracking sync error: {e}")
    
    return jsonify({'success': True, 'data': result, 'stats': tracker.get_progress_stats()})


@app.route('/tracker/water', methods=['POST'])
def add_water():
    """Add water intake"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    ml = data.get('ml', 250)  # Default glass size
    email = session['user_email']
    
    tracker = DailyTracker(email)
    result = tracker.add_water(ml)
    
    # Also save to Firebase if enabled
    if use_firebase:
        try:
            tracking_data = {
                'water_ml': ml,
                'date': datetime.now().isoformat(),
                'type': 'water_intake'
            }
            firebase.store_tracking_data(email, tracking_data)
        except Exception as e:
            print(f"Firebase tracking sync error: {e}")
    
    return jsonify({'success': True, 'data': result, 'stats': tracker.get_progress_stats()})


@app.route('/tracker/sleep', methods=['POST'])
def update_sleep():
    """Update sleep hours"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    hours = data.get('hours', 0)
    email = session['user_email']
    
    tracker = DailyTracker(email)
    result = tracker.update_sleep(hours)
    
    # Also save to Firebase if enabled
    if use_firebase:
        try:
            tracking_data = {
                'sleep_hours': hours,
                'date': datetime.now().isoformat(),
                'type': 'sleep_update'
            }
            firebase.store_tracking_data(email, tracking_data)
        except Exception as e:
            print(f"Firebase tracking sync error: {e}")
    
    return jsonify({'success': True, 'data': result, 'stats': tracker.get_progress_stats()})


@app.route('/tracker/meal/<meal_type>/<action>', methods=['POST'])
def toggle_meal(meal_type, action):
    """Mark meal as completed/uncompleted"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    email = session['user_email']
    tracker = DailyTracker(email)
    
    if action == 'complete':
        result = tracker.complete_meal(meal_type)
    elif action == 'uncomplete':
        result = tracker.uncomplete_meal(meal_type)
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    # Also save to Firebase if enabled
    if use_firebase:
        try:
            tracking_data = {
                'meal_type': meal_type,
                'action': action,
                'date': datetime.now().isoformat(),
                'type': 'meal_completion'
            }
            firebase.store_tracking_data(email, tracking_data)
        except Exception as e:
            print(f"Firebase tracking sync error: {e}")
    
    return jsonify({'success': True, 'data': result, 'stats': tracker.get_progress_stats()})


@app.route('/tracker/exercise/<day>/<exercise_name>/<action>', methods=['POST'])
def toggle_exercise(day, exercise_name, action):
    """Mark exercise as completed/uncompleted"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    email = session['user_email']
    tracker = DailyTracker(email)
    
    if action == 'complete':
        result = tracker.complete_exercise(exercise_name, day)
    elif action == 'uncomplete':
        result = tracker.uncomplete_exercise(exercise_name, day)
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    # Also save to Firebase if enabled
    if use_firebase:
        try:
            tracking_data = {
                'exercise_name': exercise_name,
                'day': day,
                'action': action,
                'date': datetime.now().isoformat(),
                'type': 'exercise_completion'
            }
            firebase.store_tracking_data(email, tracking_data)
        except Exception as e:
            print(f"Firebase tracking sync error: {e}")
    
    return jsonify({'success': True, 'data': result, 'stats': tracker.get_progress_stats()})


@app.route('/tracker/replace_food', methods=['POST'])
def replace_food():
    """Replace food item in meal plan"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.json
    meal_type = data.get('meal_type')
    original_food = data.get('original_food')
    replacement_food = data.get('replacement_food')
    
    tracker = DailyTracker(session['user_email'])
    result = tracker.replace_food(meal_type, original_food, replacement_food)
    
    return jsonify({'success': True, 'data': result})


@app.route('/tracker/weekly', methods=['GET'])
def get_weekly_summary():
    """Get weekly summary"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    tracker = DailyTracker(session['user_email'])
    weekly_data = tracker.get_weekly_summary()
    
    return jsonify({'success': True, 'data': weekly_data})


@app.route('/regenerate-advice', methods=['POST'])
def regenerate_advice():
    """Regenerate AI advice for the current plan"""
    try:
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No user profile found. Please create a profile first.'
            }), 400
        
        # Generate complete plan
        plan = system.generate_complete_plan(user_id)
        
        # Get user profile for Gemini
        user_email = session.get('user_email')
        user_profile = db.get_user_profile(user_email)
        if user_profile:
            try:
                # Initialize Gemini service
                gemini = GeminiService()
                
                # Create context for Gemini
                context = f"""
                Current Plan Summary:
                - Goal: {plan.get('goal', 'Not specified')}
                - Daily Calories: {plan.get('daily_calories', 'Not calculated')}
                - Workout Frequency: {plan.get('workout_frequency', 'Not specified')}
                - Dietary Focus: {plan.get('dietary_focus', 'Balanced')}
                """
                
                # Get AI-powered advice
                ai_advice = gemini.get_personalized_advice(
                    user_profile=user_profile,
                    context=context
                )
                
                return jsonify({
                    'success': True,
                    'ai_advice': ai_advice
                })
                
            except Exception as e:
                print(f"Warning: Could not generate AI advice: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to generate advice. Please try again.'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Please complete your profile to get personalized AI advice.'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Store user feedback on AI advice - supports both Firebase and local storage"""
    try:
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        data = request.json
        feedback_type = data.get('type')
        advice_text = data.get('advice_text', '')
        detailed_comment = data.get('detailed_comment')
        
        if not feedback_type:
            return jsonify({
                'success': False,
                'error': 'Feedback type is required'
            }), 400
        
        # Store feedback in database
        email = session['user_email']
        if use_firebase:
            # Store in Firebase using email
            firebase.store_feedback(
                uid_or_email=email,
                user_email=email,
                feedback_type=feedback_type,
                advice_text=advice_text,
                detailed_comment=detailed_comment
            )
        else:
            # Store in local database
            db.store_feedback(
                user_email=email,
                feedback_type=feedback_type,
                advice_text=advice_text,
                detailed_comment=detailed_comment
            )
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
    
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    """Save user profile to Firebase and local storage"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        profile_data = request.json
        email = session['user_email']
        
        # Save to Firebase if available
        if use_firebase:
            uid = session.get('user_uid')
            if uid:
                firebase.update_user_profile(uid, profile_data)
        
        # Also save to local database for backup
        db.update_user_profile(email, profile_data)
        
        return jsonify({'success': True, 'message': 'Profile saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-profile', methods=['GET'])
def get_profile():
    """Get user profile from Firebase or local storage"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        email = session['user_email']
        profile = None
        
        # Try local database first (most reliable)
        profile = db.get_user_profile(email)
        
        # If not in local database, try Firebase
        if not profile and use_firebase:
            profile = firebase.get_user_profile(email)
            # If found in Firebase, sync to local database
            if profile:
                db.update_user_profile(email, profile)
        
        return jsonify({'success': True, 'profile': profile})
    except Exception as e:
        print(f"Error getting profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/load-profile-data', methods=['GET'])
def load_profile_data():
    """Load complete profile data for dashboard"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        email = session['user_email']
        
        # Get user data from local database
        user = db.get_user(email)
        profile = db.get_user_profile(email)
        
        if profile:
            return jsonify({
                'success': True,
                'user': {
                    'email': email,
                    'name': user.get('name', 'User') if user else 'User',
                    'created_at': user.get('created_at') if user else None
                },
                'profile': profile,
                'source': 'local'
            })
        else:
            # Try Firebase if available
            if use_firebase and 'user_uid' in session:
                firebase_user = firebase.get_user(session['user_uid'])
                firebase_profile = firebase.get_user_profile(email)
                
                if firebase_profile:
                    # Sync to local database
                    db.update_user_profile(email, firebase_profile)
                    return jsonify({
                        'success': True,
                        'user': {
                            'email': email,
                            'name': firebase_user.get('name', 'User') if firebase_user else 'User',
                            'created_at': firebase_user.get('created_at') if firebase_user else None
                        },
                        'profile': firebase_profile,
                        'source': 'firebase'
                    })
            
            return jsonify({
                'success': False,
                'profile': None,
                'message': 'No profile found. Please create a profile first.'
            })
    except Exception as e:
        print(f"Error loading profile data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test-firebase', methods=['POST'])
def test_firebase():
    """Test Firebase connection and write capability"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        email = session['user_email']
        test_data = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'email': email
        }
        
        print(f"[TEST] Testing Firebase write for {email}")
        print(f"[TEST] Firebase initialized: {use_firebase}")
        print(f"[TEST] Firebase object: {firebase}")
        
        if use_firebase:
            result = firebase.update_user_profile(email, test_data)
            print(f"[TEST] Firebase write result: {result}")
            return jsonify({'success': True, 'message': 'Test data written to Firebase', 'firebase_enabled': True})
        else:
            return jsonify({'success': False, 'message': 'Firebase not enabled', 'firebase_enabled': False})
    except Exception as e:
        print(f"[TEST ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/feedback-stats', methods=['GET'])
def feedback_stats():
    """Get feedback statistics (admin only) - supports both Firebase and local storage"""
    try:
        if 'user_email' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login first'
            }), 401
        
        if not db.is_admin(session['user_email']):
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        # Get stats from appropriate storage
        if use_firebase:
            stats = firebase.get_feedback_stats()
        else:
            stats = db.get_feedback_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
