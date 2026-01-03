# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

print("Generating NFHS-5 based synthetic beneficiary data...\n")

# Load NFHS data for realistic distributions
nfhs_df = pd.read_csv('NFHS-5-States.csv')

# Extract Indian states from NFHS data
indian_states = nfhs_df[nfhs_df['state'] != 'India']['state'].unique()

# Sample common Indian names
first_names_male = ['Aarav', 'Vivaan', 'Aditya', 'Arjun', 'Sai', 'Arnav', 'Ayaan', 'Krishna', 'Ishaan', 'Shaurya',
                     'Atharva', 'Advaith', 'Pranav', 'Reyansh', 'Muhammad', 'Syed', 'Aryan', 'Ved', 'Kabir', 'Dhruv']
first_names_female = ['Aadhya', 'Saanvi', 'Ananya', 'Diya', 'Pari', 'Aaradhya', 'Anika', 'Sara', 'Navya', 'Angel',
                       'Aditi', 'Siya', 'Myra', 'Kiara', 'Pihu', 'Prisha', 'Riya', 'Avni', 'Ishita', 'Zoya']
last_names = ['Kumar', 'Singh', 'Sharma', 'Patel', 'Reddy', 'Rao', 'Nair', 'Iyer', 'Das', 'Gupta',
               'Khan', 'Joshi', 'Verma', 'Pandey', 'Yadav', 'Mehta', 'Desai', 'Shah', 'Malhotra', 'Chopra']

# Age group definitions based on NFHS
age_groups = ['0-2 years', '3-5 years', '6-12 years', '13-18 years']
age_ranges = {
    '0-2 years': (0, 24),      # 0-24 months
    '3-5 years': (36, 60),     # 36-60 months
    '6-12 years': (72, 144),   # 6-12 years
    '13-18 years': (156, 216)  # 13-18 years
}

# NFHS-5 based risk distributions (India average)
# From NFHS data: stunting=35.5%, wasting=19.3%, underweight=32.1%
malnutrition_rates = {
    '0-2 years': 0.40,   # Higher in younger children
    '3-5 years': 0.35,
    '6-12 years': 0.25,
    '13-18 years': 0.20
}

# Generate data
n_beneficiaries = 5000
data = []

for i in range(n_beneficiaries):
    # Demographics
    gender = np.random.choice(['Male', 'Female'], p=[0.52, 0.48])
    first_name = np.random.choice(first_names_male if gender == 'Male' else first_names_female)
    last_name = np.random.choice(last_names)
    name = f"{first_name} {last_name}"

    age_group = np.random.choice(age_groups, p=[0.25, 0.30, 0.30, 0.15])  # More in 3-12 range
    age_months = np.random.randint(age_ranges[age_group][0], age_ranges[age_group][1] + 1)

    # Region selection from actual NFHS states
    region = np.random.choice([
        'Uttar Pradesh', 'Maharashtra', 'Bihar', 'West Bengal', 'Madhya Pradesh',
        'Tamil Nadu', 'Rajasthan', 'Karnataka', 'Gujarat', 'Andhra Pradesh',
        'Odisha', 'Telangana', 'Kerala', 'Jharkhand', 'Assam',
        'Punjab', 'Chhattisgarh', 'Haryana', 'NCT Delhi', 'Jammu and Kashmir'
    ])

    # Risk-based generation using NFHS patterns
    is_high_risk = np.random.random() < malnutrition_rates[age_group]

    # Nutrition indicators
    if is_high_risk:
        meals_per_day = np.random.choice([1, 2, 3], p=[0.30, 0.50, 0.20])
        food_diversity_score = np.random.randint(1, 4)  # Low diversity
        protein_intake_g = np.random.uniform(10, 30)
        calorie_intake_kcal = np.random.uniform(800, 1400)
        attendance_rate = np.random.uniform(0.3, 0.7)
    else:
        meals_per_day = np.random.choice([2, 3, 4], p=[0.20, 0.60, 0.20])
        food_diversity_score = np.random.randint(4, 8)  # Good diversity
        protein_intake_g = np.random.uniform(35, 60)
        calorie_intake_kcal = np.random.uniform(1500, 2200)
        attendance_rate = np.random.uniform(0.75, 1.0)

    # Add some randomness
    days_since_last_check = np.random.randint(0, 45)

    # Calculate risk score (0-100) based on multiple factors
    risk_factors = []

    # Meal frequency risk
    if meals_per_day < 3:
        risk_factors.append(25)
    elif meals_per_day == 3:
        risk_factors.append(10)
    else:
        risk_factors.append(0)

    # Food diversity risk
    risk_factors.append((7 - food_diversity_score) * 5)

    # Protein intake risk
    if protein_intake_g < 30:
        risk_factors.append(20)
    elif protein_intake_g < 40:
        risk_factors.append(10)
    else:
        risk_factors.append(0)

    # Calorie intake risk (age-adjusted)
    required_calories = {
        '0-2 years': 1000,
        '3-5 years': 1400,
        '6-12 years': 1800,
        '13-18 years': 2200
    }
    calorie_deficit = max(0, (required_calories[age_group] - calorie_intake_kcal) / required_calories[age_group])
    risk_factors.append(calorie_deficit * 30)

    # Attendance risk
    if attendance_rate < 0.5:
        risk_factors.append(20)
    elif attendance_rate < 0.75:
        risk_factors.append(10)
    else:
        risk_factors.append(0)

    # Time since last check
    risk_factors.append(min(days_since_last_check / 45 * 10, 10))

    # Calculate total risk score
    risk_score = min(sum(risk_factors) + np.random.normal(0, 5), 100)
    risk_score = max(0, risk_score)

    # Risk category
    if risk_score >= 60:
        risk_category = 'High'
    elif risk_score >= 30:
        risk_category = 'Medium'
    else:
        risk_category = 'Low'

    # Generate timestamp (last 30 days)
    days_ago = np.random.randint(0, 30)
    last_updated = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

    # Compile row
    beneficiary = {
        'beneficiary_id': f'BEN{i+1:05d}',
        'name': name,
        'age_group': age_group,
        'age_months': age_months,
        'gender': gender,
        'region': region,
        'meals_per_day': meals_per_day,
        'food_diversity_score': food_diversity_score,
        'protein_intake_g': round(protein_intake_g, 1),
        'calorie_intake_kcal': round(calorie_intake_kcal, 0),
        'attendance_rate': round(attendance_rate, 2),
        'days_since_last_check': days_since_last_check,
        'risk_score': round(risk_score, 1),
        'risk_category': risk_category,
        'last_updated': last_updated
    }

    data.append(beneficiary)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('beneficiary_data.csv', index=False)

# Print statistics
print(f" Generated {len(df)} beneficiary records\n")
print("=� Statistics:")
print(f"   Total beneficiaries: {len(df):,}")
print(f"   High risk: {len(df[df['risk_category'] == 'High']):,} ({len(df[df['risk_category'] == 'High'])/len(df)*100:.1f}%)")
print(f"   Medium risk: {len(df[df['risk_category'] == 'Medium']):,} ({len(df[df['risk_category'] == 'Medium'])/len(df)*100:.1f}%)")
print(f"   Low risk: {len(df[df['risk_category'] == 'Low']):,} ({len(df[df['risk_category'] == 'Low'])/len(df)*100:.1f}%)")
print(f"   Average risk score: {df['risk_score'].mean():.1f}/100")
print(f"\n   Gender: {len(df[df['gender'] == 'Male']):,} Male, {len(df[df['gender'] == 'Female']):,} Female")
print(f"   Regions covered: {df['region'].nunique()}")
print(f"\n   Age distribution:")
for age in age_groups:
    count = len(df[df['age_group'] == age])
    print(f"      {age}: {count:,} ({count/len(df)*100:.1f}%)")

print(f"\n=� Data saved to: beneficiary_data.csv")
print(f"   Columns: {', '.join(df.columns.tolist())}")
