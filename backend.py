from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

app = FastAPI(title="NourishAI Intelligence API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
score_model = joblib.load('risk_score_model.pkl')
cat_model = joblib.load('risk_category_model.pkl')
le_age = joblib.load('encoder_age.pkl')
le_region = joblib.load('encoder_region.pkl')
le_gender = joblib.load('encoder_gender.pkl')

# Load beneficiary data
df = pd.read_csv('beneficiary_data.csv')

# Models
class MealInput(BaseModel):
    user_message: str
    language: str = "en"

class RiskInput(BaseModel):
    age_group: str
    gender: str
    region: str
    meals_per_day: int
    food_diversity_score: int
    protein_intake_g: float
    calorie_intake_kcal: float
    attendance_rate: float
    days_since_last_check: int = 0

class RiskPrediction(BaseModel):
    risk_score: float
    risk_category: str
    confidence: float
    recommendations: List[str]
    timestamp: str

# Helper functions
def extract_meals_from_text(text):
    """Simple meal extraction (can be enhanced with NLP)"""
    text_lower = text.lower()
    
    meals = []
    food_items = {
        'rice': 'cereals',
        'roti': 'cereals',
        'chapati': 'cereals',
        'dal': 'pulses',
        'lentils': 'pulses',
        'sabzi': 'vegetables',
        'vegetables': 'vegetables',
        'fruit': 'fruits',
        'banana': 'fruits',
        'apple': 'fruits',
        'milk': 'dairy',
        'curd': 'dairy',
        'egg': 'protein',
        'chicken': 'protein',
        'fish': 'protein'
    }
    
    detected_groups = set()
    for item, group in food_items.items():
        if item in text_lower:
            meals.append(item)
            detected_groups.add(group)
    
    return {
        'meals': meals,
        'food_groups': list(detected_groups),
        'diversity_score': len(detected_groups)
    }

def generate_recommendations(risk_score, input_data):
    """Generate personalized recommendations"""
    recs = []
    
    if input_data.meals_per_day < 3:
        recs.append("🍽️ Increase meal frequency to at least 3 times per day")
    
    if input_data.food_diversity_score < 4:
        recs.append("🥗 Add more variety - include vegetables, fruits, and protein sources")
    
    if input_data.protein_intake_g < 40:
        recs.append("🥚 Increase protein through dal, eggs, milk, or soy products")
    
    if input_data.attendance_rate < 0.75:
        recs.append("📅 Improve program attendance for consistent nutrition")
    
    if risk_score > 60:
        recs.append("⚠️ HIGH RISK - Schedule health checkup within 7 days")
        recs.append("📞 Contact program coordinator immediately")
    elif risk_score > 40:
        recs.append("⚡ Monitor closely - recheck within 14 days")
    
    if not recs:
        recs.append("✅ Continue current nutrition plan")
    
    return recs

# Routes
@app.get("/")
def root():
    return {
        "message": "NourishAI Intelligence API",
        "version": "1.0",
        "endpoints": ["/predict", "/chat", "/dashboard/stats", "/beneficiaries"]
    }

@app.post("/predict", response_model=RiskPrediction)
def predict_risk(input_data: RiskInput):
    """Predict nourishment risk"""
    try:
        # Encode categorical
        age_months_map = {
            '0-2 years': 12,
            '3-5 years': 48,
            '6-12 years': 108,
            '13-18 years': 180
        }
        age_months = age_months_map.get(input_data.age_group, 60)
        
        age_encoded = le_age.transform([input_data.age_group])[0]
        region_encoded = le_region.transform([input_data.region])[0]
        gender_encoded = le_gender.transform([input_data.gender])[0]
        
        # Prepare features
        features = [[
            age_months,
            input_data.meals_per_day,
            input_data.food_diversity_score,
            input_data.protein_intake_g,
            input_data.calorie_intake_kcal,
            input_data.attendance_rate,
            input_data.days_since_last_check,
            age_encoded,
            region_encoded,
            gender_encoded
        ]]
        
        # Predict
        risk_score = score_model.predict(features)[0]
        risk_category = cat_model.predict(features)[0]
        risk_proba = cat_model.predict_proba(features)[0]
        
        return RiskPrediction(
            risk_score=round(float(risk_score), 1),
            risk_category=risk_category,
            confidence=round(float(max(risk_proba)) * 100, 1),
            recommendations=generate_recommendations(risk_score, input_data),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_interface(meal_input: MealInput):
    """Simple chatbot for meal logging"""
    try:
        meal_data = extract_meals_from_text(meal_input.user_message)
        
        response = {
            "detected_meals": meal_data['meals'],
            "food_groups": meal_data['food_groups'],
            "diversity_score": meal_data['diversity_score'],
            "message": f"I detected {len(meal_data['meals'])} food items covering {meal_data['diversity_score']} food groups."
        }
        
        if meal_data['diversity_score'] < 3:
            response['suggestion'] = "Try to add more variety - include vegetables, fruits, or protein sources."
        else:
            response['suggestion'] = "Good dietary diversity! Keep it up."
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/stats")
def get_dashboard_stats():
    """Get aggregated statistics"""
    try:
        stats = {
            'total_beneficiaries': len(df),
            'high_risk_count': len(df[df['risk_category'] == 'High']),
            'medium_risk_count': len(df[df['risk_category'] == 'Medium']),
            'low_risk_count': len(df[df['risk_category'] == 'Low']),
            'avg_risk_score': round(df['risk_score'].mean(), 1),
            'regions': df['region'].unique().tolist(),
            'region_stats': df.groupby('region').agg({
                'risk_score': 'mean',
                'beneficiary_id': 'count'
            }).round(1).to_dict(),
            'risk_by_age': df.groupby('age_group')['risk_category'].value_counts().to_dict()
        }
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/beneficiaries")
def get_beneficiaries(risk_category: Optional[str] = None, limit: int = 100):
    """Get beneficiary list"""
    try:
        filtered_df = df
        if risk_category:
            filtered_df = df[df['risk_category'] == risk_category]
        
        return filtered_df.head(limit).to_dict('records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)