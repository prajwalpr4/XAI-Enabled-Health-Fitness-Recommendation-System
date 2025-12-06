"""
Diet Recommendation Engine with XAI
Provides personalized diet plans with clear explanations
"""
from typing import Dict, List, Tuple
from models.user_profile import UserProfile


class DietRecommendationEngine:
    """Generate personalized diet recommendations with explanations"""
    
    def __init__(self):
        self.macronutrient_ratios = {
            'weight_loss': {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30},
            'muscle_gain': {'protein': 0.35, 'carbs': 0.45, 'fats': 0.20},
            'maintenance': {'protein': 0.25, 'carbs': 0.45, 'fats': 0.30},
            'endurance': {'protein': 0.20, 'carbs': 0.55, 'fats': 0.25}
        }
        
        # Load food database from Kaggle dataset
        self.food_database = self._load_food_database()
        
        # Initialize SHAP explainer (lazy loading)
        self.shap_explainer = None
    
    def _get_shap_explainer(self):
        """Lazy load SHAP explainer"""
        if self.shap_explainer is None:
            try:
                from ml_shap_explainer import SHAPMLExplainer
                self.shap_explainer = SHAPMLExplainer()
                # Try to load existing model or train new one
                if not self.shap_explainer.load_model():
                    self.shap_explainer.train_model()
            except Exception as e:
                print(f"Warning: Could not load SHAP explainer: {e}")
                self.shap_explainer = None
        return self.shap_explainer
    
    def _load_food_database(self):
        """Load food database from Kaggle dataset JSON"""
        import json
        import os
        
        kaggle_db_path = 'kaggle_data/food_database.json'
        
        if os.path.exists(kaggle_db_path):
            with open(kaggle_db_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to original database if Kaggle data not available
            return self._get_default_food_database()
    
    def _get_default_food_database(self):
        """Fallback food database"""
        return {
            'chicken_breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6, 'category': 'protein'},
            'salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fats': 13, 'category': 'protein'},
            'eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fats': 11, 'category': 'protein'},
            'greek_yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fats': 0.4, 'category': 'protein'},
            'brown_rice': {'calories': 111, 'protein': 2.6, 'carbs': 23, 'fats': 0.9, 'category': 'carbs'},
            'quinoa': {'calories': 120, 'protein': 4.4, 'carbs': 21, 'fats': 1.9, 'category': 'carbs'},
            'sweet_potato': {'calories': 86, 'protein': 1.6, 'carbs': 20, 'fats': 0.1, 'category': 'carbs'},
            'oatmeal': {'calories': 389, 'protein': 17, 'carbs': 66, 'fats': 7, 'category': 'carbs'},
            'avocado': {'calories': 160, 'protein': 2, 'carbs': 9, 'fats': 15, 'category': 'fats'},
            'almonds': {'calories': 579, 'protein': 21, 'carbs': 22, 'fats': 50, 'category': 'fats'},
            'olive_oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fats': 100, 'category': 'fats'},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fats': 0.4, 'category': 'vegetables'},
            'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fats': 0.4, 'category': 'vegetables'},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fats': 0.3, 'category': 'fruits'},
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fats': 0.2, 'category': 'fruits'}
        }
    
    def generate_recommendations(self, user: UserProfile) -> Dict:
        """Generate personalized diet recommendations"""
        # Determine calorie target based on goals
        calorie_target = self._calculate_calorie_target(user)
        
        # Determine macronutrient distribution
        macro_distribution = self._calculate_macro_distribution(user)
        
        # Generate meal plan
        meal_plan = self._generate_meal_plan(calorie_target, macro_distribution, user)
        
        # Generate explanations with SHAP
        explanations = self._generate_explanations_with_shap(user, calorie_target, macro_distribution)
        
        return {
            'calorie_target': calorie_target,
            'macro_distribution': macro_distribution,
            'meal_plan': meal_plan,
            'explanations': explanations,
            'recommendations': self._generate_dietary_tips(user)
        }
    
    def _calculate_calorie_target(self, user: UserProfile) -> float:
        """Calculate target calories based on goals"""
        base_tdee = user.tdee or 2000
        
        # Adjust based on primary goal
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        adjustments = {
            'weight_loss': -500,  # 500 calorie deficit
            'muscle_gain': +300,  # 300 calorie surplus
            'maintenance': 0,
            'endurance': +200
        }
        
        return round(base_tdee + adjustments.get(primary_goal, 0), 2)
    
    def _calculate_macro_distribution(self, user: UserProfile) -> Dict:
        """Calculate macronutrient distribution"""
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        ratios = self.macronutrient_ratios.get(primary_goal, self.macronutrient_ratios['maintenance'])
        
        calorie_target = self._calculate_calorie_target(user)
        
        return {
            'protein_g': round((calorie_target * ratios['protein']) / 4, 1),  # 4 cal/g
            'carbs_g': round((calorie_target * ratios['carbs']) / 4, 1),
            'fats_g': round((calorie_target * ratios['fats']) / 9, 1),  # 9 cal/g
            'protein_percent': int(ratios['protein'] * 100),
            'carbs_percent': int(ratios['carbs'] * 100),
            'fats_percent': int(ratios['fats'] * 100)
        }
    
    def _generate_meal_plan(self, calorie_target: float, macro_dist: Dict, user: UserProfile) -> Dict:
        """Generate sample meal plan"""
        # Filter foods based on dietary restrictions
        available_foods = self._filter_foods(user.dietary_restrictions)
        
        meals = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': []
        }
        
        # Helper function to check if food is available
        def use_food(food_name, default_alternative=None):
            if food_name in available_foods:
                return food_name
            elif default_alternative and default_alternative in available_foods:
                return default_alternative
            return None
        
        # Simple meal plan generation based on dietary restrictions
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        
        if primary_goal == 'muscle_gain':
            # Breakfast
            if use_food('eggs'):
                meals['breakfast'].append({'food': 'eggs', 'quantity': 150, 'unit': 'g'})
            elif use_food('paneer'):
                meals['breakfast'].append({'food': 'paneer', 'quantity': 100, 'unit': 'g'})
            elif use_food('tofu'):
                meals['breakfast'].append({'food': 'tofu', 'quantity': 150, 'unit': 'g'})
            
            carb = use_food('oatmeal') or use_food('poha') or use_food('upma') or use_food('brown_rice')
            if carb:
                meals['breakfast'].append({'food': carb, 'quantity': 60, 'unit': 'g'})
            
            if use_food('banana'):
                meals['breakfast'].append({'food': 'banana', 'quantity': 100, 'unit': 'g'})
            
            # Lunch
            protein = use_food('chicken_curry') or use_food('chicken_breast') or use_food('paneer') or use_food('dal_tadka') or use_food('tofu')
            if protein:
                meals['lunch'].append({'food': protein, 'quantity': 200, 'unit': 'g'})
            
            carb = use_food('basmati_rice') or use_food('brown_rice') or use_food('roti')
            if carb:
                quantity = 150 if 'rice' in carb else 100
                meals['lunch'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('broccoli'):
                meals['lunch'].append({'food': 'broccoli', 'quantity': 150, 'unit': 'g'})
            
            # Dinner
            protein = use_food('fish_curry') or use_food('salmon') or use_food('rajma') or use_food('chana_masala') or use_food('lentils')
            if protein:
                meals['dinner'].append({'food': protein, 'quantity': 180, 'unit': 'g'})
            
            carb = use_food('chapati') or use_food('roti') or use_food('sweet_potato')
            if carb:
                quantity = 100 if 'chapati' in carb or 'roti' in carb else 200
                meals['dinner'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('spinach'):
                meals['dinner'].append({'food': 'spinach', 'quantity': 100, 'unit': 'g'})
            
            # Snacks
            snack = use_food('curd') or use_food('greek_yogurt') or use_food('cashews') or use_food('almonds')
            if snack:
                quantity = 150 if 'curd' in snack or 'yogurt' in snack else 30
                meals['snacks'].append({'food': snack, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('almonds') or use_food('peanuts'):
                nut = use_food('almonds') or use_food('peanuts')
                meals['snacks'].append({'food': nut, 'quantity': 30, 'unit': 'g'})
        
        elif primary_goal == 'weight_loss':
            # Breakfast
            breakfast_protein = use_food('curd') or use_food('greek_yogurt') or use_food('moong_dal') or use_food('tofu')
            if breakfast_protein:
                meals['breakfast'].append({'food': breakfast_protein, 'quantity': 200, 'unit': 'g'})
            
            if use_food('apple'):
                meals['breakfast'].append({'food': 'apple', 'quantity': 150, 'unit': 'g'})
            
            # Lunch
            protein = use_food('chicken_curry') or use_food('chicken_breast') or use_food('paneer') or use_food('dal_tadka') or use_food('tofu')
            if protein:
                meals['lunch'].append({'food': protein, 'quantity': 150, 'unit': 'g'})
            
            carb = use_food('roti') or use_food('chapati') or use_food('quinoa')
            if carb:
                quantity = 75 if 'roti' in carb or 'chapati' in carb else 100
                meals['lunch'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('broccoli'):
                meals['lunch'].append({'food': 'broccoli', 'quantity': 200, 'unit': 'g'})
            
            # Dinner
            protein = use_food('fish_curry') or use_food('salmon') or use_food('moong_dal') or use_food('rajma') or use_food('lentils')
            if protein:
                meals['dinner'].append({'food': protein, 'quantity': 150, 'unit': 'g'})
            
            carb = use_food('chapati') or use_food('sweet_potato')
            if carb:
                quantity = 75 if 'chapati' in carb else 150
                meals['dinner'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('spinach'):
                meals['dinner'].append({'food': 'spinach', 'quantity': 150, 'unit': 'g'})
            
            # Snacks
            if use_food('almonds') or use_food('peanuts'):
                nut = use_food('almonds') or use_food('peanuts')
                meals['snacks'].append({'food': nut, 'quantity': 20, 'unit': 'g'})
        
        else:  # maintenance or endurance
            # Breakfast
            if use_food('eggs'):
                meals['breakfast'].append({'food': 'eggs', 'quantity': 120, 'unit': 'g'})
            elif use_food('paneer'):
                meals['breakfast'].append({'food': 'paneer', 'quantity': 80, 'unit': 'g'})
            elif use_food('tofu'):
                meals['breakfast'].append({'food': 'tofu', 'quantity': 120, 'unit': 'g'})
            
            carb = use_food('oatmeal') or use_food('upma') or use_food('poha') or use_food('brown_rice')
            if carb:
                meals['breakfast'].append({'food': carb, 'quantity': 80, 'unit': 'g'})
            
            if use_food('banana'):
                meals['breakfast'].append({'food': 'banana', 'quantity': 100, 'unit': 'g'})
            
            # Lunch
            protein = use_food('chicken_curry') or use_food('chicken_breast') or use_food('paneer') or use_food('dal_tadka') or use_food('tofu')
            if protein:
                meals['lunch'].append({'food': protein, 'quantity': 170, 'unit': 'g'})
            
            carb = use_food('basmati_rice') or use_food('brown_rice') or use_food('roti')
            if carb:
                quantity = 130 if 'rice' in carb else 90
                meals['lunch'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('broccoli'):
                meals['lunch'].append({'food': 'broccoli', 'quantity': 150, 'unit': 'g'})
            
            if use_food('avocado'):
                meals['lunch'].append({'food': 'avocado', 'quantity': 50, 'unit': 'g'})
            
            # Dinner
            protein = use_food('fish_curry') or use_food('salmon') or use_food('rajma') or use_food('chana_masala') or use_food('lentils')
            if protein:
                meals['dinner'].append({'food': protein, 'quantity': 160, 'unit': 'g'})
            
            carb = use_food('chapati') or use_food('quinoa') or use_food('roti')
            if carb:
                quantity = 90 if 'chapati' in carb or 'roti' in carb else 120
                meals['dinner'].append({'food': carb, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('spinach'):
                meals['dinner'].append({'food': 'spinach', 'quantity': 100, 'unit': 'g'})
            
            # Snacks
            snack = use_food('curd') or use_food('greek_yogurt') or use_food('cashews') or use_food('almonds')
            if snack:
                quantity = 100 if 'curd' in snack or 'yogurt' in snack else 25
                meals['snacks'].append({'food': snack, 'quantity': quantity, 'unit': 'g'})
            
            if use_food('almonds') or use_food('peanuts'):
                nut = use_food('almonds') or use_food('peanuts')
                meals['snacks'].append({'food': nut, 'quantity': 25, 'unit': 'g'})
        
        # Calculate nutritional totals
        totals = self._calculate_meal_totals(meals)
        
        return {
            'meals': meals,
            'daily_totals': totals
        }
    
    def _filter_foods(self, restrictions: List[str]) -> List[str]:
        """Filter foods based on dietary restrictions"""
        if not restrictions:
            return list(self.food_database.keys())
        
        # Define food categories
        non_veg_foods = ['chicken_breast', 'turkey_breast', 'salmon', 'tuna', 'chicken_curry', 'fish_curry']
        vegetarian_excluded = non_veg_foods  # Vegetarians exclude meat/fish
        vegan_excluded = non_veg_foods + ['eggs', 'greek_yogurt', 'cottage_cheese', 'whey_protein', 'paneer', 'curd']  # Vegans exclude meat/fish/dairy/eggs
        
        filtered = list(self.food_database.keys())
        
        # Handle dietary preferences
        if 'vegan' in restrictions:
            # Vegan: exclude meat, fish, dairy, and eggs
            filtered = [f for f in filtered if f not in vegan_excluded]
        elif 'vegetarian' in restrictions:
            # Vegetarian: exclude meat and fish
            filtered = [f for f in filtered if f not in vegetarian_excluded]
        elif 'non_veg' in restrictions:
            # Non-veg only: exclude vegetarian protein sources, keep only meat/fish for protein
            # Keep meat/fish, but replace vegetarian proteins like tofu, lentils
            veg_proteins = ['tofu', 'lentils', 'dal_tadka', 'moong_dal', 'chana_masala', 'rajma']
            filtered = [f for f in filtered if f not in veg_proteins]
        
        if 'gluten_free' in restrictions:
            filtered = [f for f in filtered if f not in ['oatmeal', 'whole_wheat_bread', 'pasta', 'roti', 'chapati', 'paratha']]
        
        return filtered
    
    def _calculate_meal_totals(self, meals: Dict) -> Dict:
        """Calculate total nutrition from meal plan"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
        
        for meal_type, items in meals.items():
            for item in items:
                food = item['food']
                quantity = item['quantity'] / 100  # Convert to per 100g
                
                if food in self.food_database:
                    food_data = self.food_database[food]
                    totals['calories'] += food_data['calories'] * quantity
                    totals['protein'] += food_data['protein'] * quantity
                    totals['carbs'] += food_data['carbs'] * quantity
                    totals['fats'] += food_data['fats'] * quantity
        
        return {k: round(v, 1) for k, v in totals.items()}
    
    def _generate_explanations(self, user: UserProfile, calorie_target: float, macro_dist: Dict) -> Dict:
        """Generate XAI explanations for recommendations"""
        explanations = {
            'calorie_explanation': [],
            'macro_explanation': [],
            'feature_importance': {},
            'decision_factors': []
        }
        
        # Calorie explanation
        explanations['calorie_explanation'].append(
            f"Your basal metabolic rate (BMR) is {user.bmr} calories - this is what your body burns at rest."
        )
        explanations['calorie_explanation'].append(
            f"With your {user.activity_level.replace('_', ' ')} lifestyle, your total daily energy expenditure (TDEE) is {user.tdee} calories."
        )
        
        primary_goal = user.fitness_goals[0] if user.fitness_goals else 'maintenance'
        if primary_goal == 'weight_loss':
            explanations['calorie_explanation'].append(
                f"To lose weight safely (0.5-1 kg/week), we've created a 500 calorie deficit, targeting {calorie_target} calories/day."
            )
        elif primary_goal == 'muscle_gain':
            explanations['calorie_explanation'].append(
                f"To build muscle, we've added a 300 calorie surplus, targeting {calorie_target} calories/day."
            )
        else:
            explanations['calorie_explanation'].append(
                f"For {primary_goal.replace('_', ' ')}, your target is {calorie_target} calories/day."
            )
        
        # Macro explanation
        explanations['macro_explanation'].append(
            f"Protein ({macro_dist['protein_percent']}%): {macro_dist['protein_g']}g - Essential for muscle repair and growth, especially important for your {primary_goal.replace('_', ' ')} goal."
        )
        explanations['macro_explanation'].append(
            f"Carbohydrates ({macro_dist['carbs_percent']}%): {macro_dist['carbs_g']}g - Primary energy source for your {user.activity_level.replace('_', ' ')} lifestyle."
        )
        explanations['macro_explanation'].append(
            f"Fats ({macro_dist['fats_percent']}%): {macro_dist['fats_g']}g - Crucial for hormone production and nutrient absorption."
        )
        
        # Feature importance (XAI component)
        bmi_importance = round(abs(25 - (user.bmi or 25)) / 25 * 0.15, 3)
        explanations['feature_importance'] = {
            'bmi': max(0.05, bmi_importance),  # Ensure minimum 5% contribution
            'age': round(user.age / 100 * 0.12, 3),
            'weight': round(user.weight / 150 * 0.22, 3),
            'height': round(user.height / 200 * 0.08, 3),
            'activity_level': 0.28,
            'fitness_goal': 0.18
        }
        
        # Decision factors
        explanations['decision_factors'] = [
            {
                'factor': 'Age',
                'value': f"{user.age} years",
                'impact': 'Medium',
                'explanation': f"Age {user.age} affects metabolic rate and calorie requirements."
            },
            {
                'factor': 'Weight',
                'value': f"{user.weight} kg",
                'impact': 'High',
                'explanation': f"Your weight of {user.weight} kg is a primary factor in calculating daily calorie needs."
            },
            {
                'factor': 'Height',
                'value': f"{user.height} cm",
                'impact': 'Medium',
                'explanation': f"Height of {user.height} cm influences BMI calculation and metabolic rate."
            },
            {
                'factor': 'BMI Category',
                'value': user.get_bmi_category(),
                'impact': 'High' if (user.bmi or 25) < 18.5 or (user.bmi or 25) > 30 else 'Medium',
                'explanation': f"Your BMI of {user.bmi} indicates {user.get_bmi_category()}, influencing calorie recommendations."
            },
            {
                'factor': 'Activity Level',
                'value': user.activity_level.replace('_', ' ').title(),
                'impact': 'High',
                'explanation': f"{user.activity_level.replace('_', ' ').title()} lifestyle increases daily calorie needs significantly."
            },
            {
                'factor': 'Fitness Goal',
                'value': primary_goal.replace('_', ' ').title(),
                'impact': 'High',
                'explanation': f"{primary_goal.replace('_', ' ').title()} goal determines calorie surplus/deficit and macro distribution."
            }
        ]
        
        return explanations
    
    def _generate_explanations_with_shap(self, user: UserProfile, calorie_target: float, macro_dist: Dict) -> Dict:
        """Generate XAI explanations with SHAP ML insights"""
        # Get base explanations
        explanations = self._generate_explanations(user, calorie_target, macro_dist)
        
        # Try to add SHAP-based insights
        explainer = self._get_shap_explainer()
        if explainer:
            try:
                shap_result = explainer.explain_recommendation(user)
                
                # Replace feature importance with SHAP values
                explanations['feature_importance'] = shap_result['feature_importance']
                explanations['shap_values'] = shap_result['shap_values']
                explanations['ml_prediction'] = shap_result['ml_prediction']
                
                # Add SHAP explanations to calorie explanation
                if shap_result['explanation']:
                    explanations['shap_insights'] = shap_result['explanation']
                    explanations['calorie_explanation'].extend([
                        "",
                        "🤖 ML-Powered Insights (SHAP Analysis):"
                    ])
                    explanations['calorie_explanation'].extend(shap_result['explanation'])
            except Exception as e:
                print(f"SHAP explanation failed: {e}")
        
        return explanations
    
    def _generate_dietary_tips(self, user: UserProfile) -> List[str]:
        """Generate personalized dietary tips"""
        tips = []
        
        bmi = user.bmi or 25
        sleep_hours = user.sleep_hours or 7.0
        
        if bmi < 18.5:
            tips.append("Focus on nutrient-dense, calorie-rich foods to reach a healthy weight.")
        elif bmi > 30:
            tips.append("Emphasize whole foods and portion control for sustainable weight loss.")
        
        if 'weight_loss' in user.fitness_goals:
            tips.append("Drink water before meals to increase satiety and reduce calorie intake.")
            tips.append("Include protein in every meal to preserve muscle mass during weight loss.")
        
        if 'muscle_gain' in user.fitness_goals:
            tips.append("Consume protein within 2 hours post-workout for optimal muscle recovery.")
            tips.append("Spread protein intake evenly throughout the day (20-30g per meal).")
        
        # Sleep-based tips
        if sleep_hours < 7:
            tips.append(f"⚠️ Your {sleep_hours} hours of sleep may increase hunger hormones (ghrelin) and reduce metabolism. Aim for 7-9 hours.")
            tips.append("Poor sleep can lead to increased cravings for high-calorie foods. Prioritize sleep hygiene.")
        elif sleep_hours >= 8:
            tips.append(f"✅ Your {sleep_hours} hours of sleep supports optimal metabolism and muscle recovery!")
        
        tips.append("Stay hydrated: aim for 8-10 glasses of water daily.")
        tips.append("Plan meals ahead to avoid impulsive, unhealthy choices.")
        
        return tips
