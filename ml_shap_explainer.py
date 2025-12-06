"""
SHAP-based ML Explainer
Uses machine learning with SHAP for accurate feature importance
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import shap
import json
import os


class SHAPMLExplainer:
    """ML model with SHAP explanations for calorie recommendations"""
    
    def __init__(self):
        self.model = None
        self.explainer = None
        self.feature_names = ['age', 'weight', 'height', 'bmi', 'gender', 'activity_level', 'goal']
        self.model_path = 'models/calorie_model.pkl'
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic training data based on BMR/TDEE formulas"""
        np.random.seed(42)
        
        data = {
            'age': np.random.randint(18, 70, n_samples),
            'weight': np.random.uniform(50, 120, n_samples),
            'height': np.random.uniform(150, 200, n_samples),
            'gender': np.random.choice([0, 1], n_samples),  # 0=female, 1=male
            'activity_level': np.random.choice([1.2, 1.375, 1.55, 1.725, 1.9], n_samples),
            'goal': np.random.choice([-500, 0, 300], n_samples)  # weight_loss, maintenance, muscle_gain
        }
        
        df = pd.DataFrame(data)
        
        # Calculate BMI
        df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
        
        # Calculate target calories using Mifflin-St Jeor
        df['bmr'] = np.where(
            df['gender'] == 1,
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] + 5,
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] - 161
        )
        
        df['tdee'] = df['bmr'] * df['activity_level']
        df['target_calories'] = df['tdee'] + df['goal']
        
        return df
    
    def train_model(self):
        """Train Random Forest model"""
        print("Generating training data...")
        df = self.generate_training_data(n_samples=2000)
        
        X = df[self.feature_names]
        y = df['target_calories']
        
        print("Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        score = self.model.score(X_test, y_test)
        print(f"Model R² Score: {score:.4f}")
        
        # Create SHAP explainer
        print("Creating SHAP explainer...")
        self.explainer = shap.TreeExplainer(self.model)
        
        return score
    
    def get_shap_values(self, user_data):
        """Get SHAP values for a user"""
        if self.model is None or self.explainer is None:
            self.train_model()
        
        # Prepare user data
        X = pd.DataFrame([user_data], columns=self.feature_names)
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        
        return {
            'prediction': float(prediction),
            'shap_values': {
                feature: float(shap_values[0][i])
                for i, feature in enumerate(self.feature_names)
            },
            'base_value': float(self.explainer.expected_value)
        }
    
    def explain_recommendation(self, user_profile):
        """Generate SHAP-based explanation for user"""
        # Encode user data
        gender_encoded = 1 if user_profile.gender.lower() == 'male' else 0
        
        activity_map = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        activity_encoded = activity_map.get(user_profile.activity_level, 1.2)
        
        goal_map = {
            'weight_loss': -500,
            'muscle_gain': 300,
            'maintenance': 0,
            'endurance': 200
        }
        primary_goal = user_profile.fitness_goals[0] if user_profile.fitness_goals else 'maintenance'
        goal_encoded = goal_map.get(primary_goal, 0)
        
        user_data = {
            'age': user_profile.age,
            'weight': user_profile.weight,
            'height': user_profile.height,
            'bmi': user_profile.bmi or 25,
            'gender': gender_encoded,
            'activity_level': activity_encoded,
            'goal': goal_encoded
        }
        
        # Get SHAP explanation
        shap_result = self.get_shap_values(user_data)
        
        # Generate human-readable explanation
        explanation = self._generate_human_explanation(shap_result, user_profile)
        
        return {
            'ml_prediction': shap_result['prediction'],
            'shap_values': shap_result['shap_values'],
            'base_value': shap_result['base_value'],
            'feature_importance': self._calculate_feature_importance(shap_result['shap_values']),
            'explanation': explanation
        }
    
    def _calculate_feature_importance(self, shap_values):
        """Calculate normalized feature importance from SHAP values"""
        # Use absolute SHAP values for importance
        abs_values = {k: abs(v) for k, v in shap_values.items()}
        total = sum(abs_values.values())
        
        if total == 0:
            return {k: 0 for k in abs_values.keys()}
        
        return {k: round(v / total, 3) for k, v in abs_values.items()}
    
    def _generate_human_explanation(self, shap_result, user_profile):
        """Generate human-readable explanation"""
        shap_values = shap_result['shap_values']
        
        # Sort features by absolute SHAP value
        sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        
        explanations = []
        
        for feature, value in sorted_features[:3]:  # Top 3 features
            if abs(value) < 10:  # Ignore negligible features
                continue
            
            direction = "increases" if value > 0 else "decreases"
            impact = abs(value)
            
            if feature == 'age':
                explanations.append(
                    f"Your age ({user_profile.age} years) {direction} calorie needs by {impact:.0f} calories. "
                    f"{'Younger individuals generally have higher metabolic rates.' if value > 0 else 'Metabolism naturally slows with age.'}"
                )
            elif feature == 'weight':
                explanations.append(
                    f"Your weight ({user_profile.weight}kg) {direction} calorie needs by {impact:.0f} calories. "
                    f"Heavier bodies require more energy to maintain."
                )
            elif feature == 'height':
                explanations.append(
                    f"Your height ({user_profile.height}cm) {direction} calorie needs by {impact:.0f} calories. "
                    f"Taller individuals have larger body surface area and higher energy requirements."
                )
            elif feature == 'bmi':
                explanations.append(
                    f"Your BMI ({user_profile.bmi:.1f}) {direction} calorie recommendations by {impact:.0f} calories. "
                    f"This reflects your body composition's impact on metabolism."
                )
            elif feature == 'activity_level':
                explanations.append(
                    f"Your {user_profile.activity_level.replace('_', ' ')} lifestyle {direction} calorie needs by {impact:.0f} calories. "
                    f"Physical activity significantly impacts daily energy expenditure."
                )
            elif feature == 'goal':
                goal_name = user_profile.fitness_goals[0] if user_profile.fitness_goals else 'maintenance'
                explanations.append(
                    f"Your {goal_name.replace('_', ' ')} goal {direction} calorie target by {impact:.0f} calories. "
                    f"This adjustment helps you achieve your desired outcome."
                )
        
        return explanations
    
    def save_model(self):
        """Save trained model"""
        import pickle
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.model, self.explainer), f)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load saved model"""
        import pickle
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model, self.explainer = pickle.load(f)
            print("Model loaded successfully")
            return True
        return False


if __name__ == "__main__":
    # Train and test the model
    explainer = SHAPMLExplainer()
    
    print("="*60)
    print("SHAP ML EXPLAINER - TRAINING")
    print("="*60)
    
    score = explainer.train_model()
    
    print("\n" + "="*60)
    print("MODEL TRAINED SUCCESSFULLY!")
    print("="*60)
    print(f"R² Score: {score:.4f}")
    print("Features:", explainer.feature_names)
    
    # Save model
    explainer.save_model()
    
    # Test with sample user
    print("\n" + "="*60)
    print("SAMPLE PREDICTION")
    print("="*60)
    
    sample_user = {
        'age': 30,
        'weight': 75,
        'height': 175,
        'bmi': 24.5,
        'gender': 1,  # male
        'activity_level': 1.55,  # moderately active
        'goal': -500  # weight loss
    }
    
    result = explainer.get_shap_values(sample_user)
    
    print(f"\nPredicted Calories: {result['prediction']:.0f}")
    print(f"Base Value: {result['base_value']:.0f}")
    print("\nSHAP Values (Feature Contributions):")
    for feature, value in result['shap_values'].items():
        print(f"  {feature:15s}: {value:+8.2f}")
    
    print("\nFeature Importance:")
    importance = explainer._calculate_feature_importance(result['shap_values'])
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature:15s}: {imp*100:5.1f}%")
