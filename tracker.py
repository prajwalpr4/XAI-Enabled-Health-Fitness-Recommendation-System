"""
Daily Health & Fitness Tracker
Track steps, water intake, meals, exercises, and progress
"""
from datetime import datetime, date
from typing import Dict, List
import json
import os


class DailyTracker:
    """Track daily health and fitness activities"""
    
    def __init__(self, user_email):
        self.user_email = user_email
        self.tracker_file = f'tracker_data/{user_email.replace("@", "_").replace(".", "_")}.json'
        self.data = self._load_tracker_data()
    
    def _load_tracker_data(self):
        """Load tracker data from file"""
        os.makedirs('tracker_data', exist_ok=True)
        
        if os.path.exists(self.tracker_file):
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def _save_tracker_data(self):
        """Save tracker data to file"""
        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_today_key(self):
        """Get today's date key"""
        return date.today().isoformat()
    
    def get_today_data(self):
        """Get today's tracking data"""
        today = self.get_today_key()
        
        if today not in self.data:
            self.data[today] = {
                'steps': 0,
                'water_ml': 0,
                'sleep_hours': 0,
                'meals_completed': [],
                'exercises_completed': [],
                'diet_replacements': {},
                'notes': '',
                'created_at': datetime.now().isoformat()
            }
            self._save_tracker_data()
        
        return self.data[today]
    
    def update_steps(self, steps):
        """Update step count"""
        today_data = self.get_today_data()
        today_data['steps'] = steps
        self._save_tracker_data()
        return today_data
    
    def add_water(self, ml):
        """Add water intake"""
        today_data = self.get_today_data()
        today_data['water_ml'] += ml
        self._save_tracker_data()
        return today_data
    
    def update_sleep(self, hours):
        """Update sleep hours"""
        today_data = self.get_today_data()
        today_data['sleep_hours'] = hours
        self._save_tracker_data()
        return today_data
    
    def complete_meal(self, meal_type):
        """Mark meal as completed"""
        today_data = self.get_today_data()
        if meal_type not in today_data['meals_completed']:
            today_data['meals_completed'].append(meal_type)
        self._save_tracker_data()
        return today_data
    
    def uncomplete_meal(self, meal_type):
        """Unmark meal"""
        today_data = self.get_today_data()
        if meal_type in today_data['meals_completed']:
            today_data['meals_completed'].remove(meal_type)
        self._save_tracker_data()
        return today_data
    
    def replace_food(self, meal_type, original_food, replacement_food):
        """Replace a food item in meal plan"""
        today_data = self.get_today_data()
        
        if meal_type not in today_data['diet_replacements']:
            today_data['diet_replacements'][meal_type] = {}
        
        today_data['diet_replacements'][meal_type][original_food] = replacement_food
        self._save_tracker_data()
        return today_data
    
    def complete_exercise(self, exercise_name, day=None):
        """Mark exercise as completed"""
        today_data = self.get_today_data()
        exercise_key = f"{day}_{exercise_name}" if day else exercise_name
        
        if exercise_key not in today_data['exercises_completed']:
            today_data['exercises_completed'].append(exercise_key)
        self._save_tracker_data()
        return today_data
    
    def uncomplete_exercise(self, exercise_name, day=None):
        """Unmark exercise"""
        today_data = self.get_today_data()
        exercise_key = f"{day}_{exercise_name}" if day else exercise_name
        
        if exercise_key in today_data['exercises_completed']:
            today_data['exercises_completed'].remove(exercise_key)
        self._save_tracker_data()
        return today_data
    
    def add_note(self, note):
        """Add daily note"""
        today_data = self.get_today_data()
        today_data['notes'] = note
        self._save_tracker_data()
        return today_data
    
    def get_weekly_summary(self):
        """Get weekly summary (Monday to Sunday)"""
        from datetime import timedelta
        
        today = date.today()
        # Get Monday of current week (0 = Monday, 6 = Sunday)
        monday = today - timedelta(days=today.weekday())
        
        weekly_data = []
        
        # Get data for Monday to Sunday
        for i in range(7):
            day = monday + timedelta(days=i)
            day_key = day.isoformat()
            
            if day_key in self.data:
                day_data = self.data[day_key].copy()
                day_data['date'] = day_key
                weekly_data.append(day_data)
            else:
                weekly_data.append({
                    'date': day_key,
                    'steps': 0,
                    'water_ml': 0,
                    'meals_completed': [],
                    'exercises_completed': []
                })
        
        return weekly_data
    
    def get_today_stats(self):
        """Get today's stats for real-time updates"""
        today_data = self.get_today_data()
        return {
            'steps': today_data['steps'],
            'water': today_data['water_ml'],
            'sleep': today_data['sleep_hours'],
            'calories': 0  # Placeholder for future use
        }
    
    def get_progress_stats(self):
        """Calculate progress statistics"""
        today_data = self.get_today_data()
        
        # Steps goal (10,000 steps recommended)
        steps_goal = 10000
        steps_progress = min(100, (today_data['steps'] / steps_goal) * 100) if steps_goal > 0 else 0
        
        # Water goal (2000ml recommended)
        water_goal = 2000
        water_progress = min(100, (today_data['water_ml'] / water_goal) * 100) if water_goal > 0 else 0
        
        # Meals completed (4 meals: breakfast, lunch, dinner, snacks)
        total_meals = 4
        meals_progress = (len(today_data['meals_completed']) / total_meals) * 100
        
        # Weekly average
        weekly_data = self.get_weekly_summary()
        avg_steps = sum(d['steps'] for d in weekly_data) / len(weekly_data) if weekly_data else 0
        avg_water = sum(d['water_ml'] for d in weekly_data) / len(weekly_data) if weekly_data else 0
        avg_sleep = sum(d.get('sleep_hours', 0) for d in weekly_data) / len(weekly_data) if weekly_data else 0
        
        return {
            'today': {
                'steps': today_data['steps'],
                'steps_goal': steps_goal,
                'steps_progress': round(steps_progress, 1),
                'water_ml': today_data['water_ml'],
                'water_goal': water_goal,
                'water_progress': round(water_progress, 1),
                'sleep_hours': today_data['sleep_hours'],
                'meals_completed': len(today_data['meals_completed']),
                'meals_total': total_meals,
                'meals_progress': round(meals_progress, 1),
                'exercises_completed': len(today_data['exercises_completed'])
            },
            'weekly': {
                'avg_steps': round(avg_steps),
                'avg_water': round(avg_water),
                'avg_sleep': round(avg_sleep, 1),
                'total_days': len(weekly_data)
            }
        }
