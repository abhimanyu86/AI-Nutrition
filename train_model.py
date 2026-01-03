import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, mean_absolute_error
import joblib

# Load data
df = pd.read_csv('beneficiary_data.csv')

print("Training Risk Prediction Model...\n")

# Prepare features
feature_cols = ['age_months', 'meals_per_day', 'food_diversity_score', 
                'protein_intake_g', 'calorie_intake_kcal', 'attendance_rate',
                'days_since_last_check']

# Encode categorical variables
le_age = LabelEncoder()
le_region = LabelEncoder()
le_gender = LabelEncoder()

df['age_group_encoded'] = le_age.fit_transform(df['age_group'])
df['region_encoded'] = le_region.fit_transform(df['region'])
df['gender_encoded'] = le_gender.fit_transform(df['gender'])

feature_cols_encoded = feature_cols + ['age_group_encoded', 'region_encoded', 'gender_encoded']

X = df[feature_cols_encoded]
y_score = df['risk_score']
y_category = df['risk_category']

# Split data
X_train, X_test, y_score_train, y_score_test, y_cat_train, y_cat_test = \
    train_test_split(X, y_score, y_category, test_size=0.2, random_state=42)

# Train Risk Score Regressor
print("Training Risk Score Predictor...")
score_model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
score_model.fit(X_train, y_score_train)

# Evaluate
y_pred_score = score_model.predict(X_test)
mae = mean_absolute_error(y_score_test, y_pred_score)
print(f"✅ Risk Score MAE: {mae:.2f}")
print(f"   Average prediction error: ±{mae:.1f} points\n")

# Train Risk Category Classifier
print("Training Risk Category Classifier...")
cat_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
cat_model.fit(X_train, y_cat_train)

# Evaluate
y_pred_cat = cat_model.predict(X_test)
print("✅ Classification Report:")
print(classification_report(y_cat_test, y_pred_cat))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols_encoded,
    'importance': score_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n📊 Top Features for Risk Prediction:")
print(feature_importance.head(5))

# Save models and encoders
joblib.dump(score_model, 'risk_score_model.pkl')
joblib.dump(cat_model, 'risk_category_model.pkl')
joblib.dump(le_age, 'encoder_age.pkl')
joblib.dump(le_region, 'encoder_region.pkl')
joblib.dump(le_gender, 'encoder_gender.pkl')

print("\n✅ Models saved successfully!")