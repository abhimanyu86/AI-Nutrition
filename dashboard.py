import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="NourishAI Intelligence", layout="wide", page_icon="🍎")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .high-risk {
        color: #ff4444;
        font-weight: bold;
    }
    .medium-risk {
        color: #ffaa00;
        font-weight: bold;
    }
    .low-risk {
        color: #44ff44;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Load data
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv('beneficiary_data.csv')

@st.cache_data(ttl=60)
def get_stats():
    response = requests.get(f"{API_URL}/dashboard/stats")
    return response.json()

# Header
st.markdown('<div class="main-header">🍎 NourishAI Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown("**Real-time Nourishment Risk Intelligence for Food Programs**")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Beneficiary Chat", "🔍 Risk Checker"])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    df = load_data()
    stats = get_stats()
    
    # Top metrics
    st.subheader("📈 Overview Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Beneficiaries", f"{stats['total_beneficiaries']:,}")
    
    with col2:
        high_pct = (stats['high_risk_count'] / stats['total_beneficiaries'] * 100)
        st.metric("🔴 High Risk", stats['high_risk_count'], 
                 delta=f"{high_pct:.1f}%", delta_color="inverse")
    
    with col3:
        st.metric("🟡 Medium Risk", stats['medium_risk_count'])
    
    with col4:
        st.metric("🟢 Low Risk", stats['low_risk_count'])
    
    with col5:
        st.metric("Avg Risk Score", f"{stats['avg_risk_score']}/100")
    
    st.markdown("---")
    
    # Risk distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Risk Distribution")
        risk_counts = df['risk_category'].value_counts()
        fig_pie = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            color=risk_counts.index,
            color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'},
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📍 Risk by Region")
        region_risk = df.groupby('region')['risk_score'].mean().sort_values(ascending=False)
        fig_region = px.bar(
            x=region_risk.values,
            y=region_risk.index,
            orientation='h',
            color=region_risk.values,
            color_continuous_scale='RdYlGn_r',
            labels={'x': 'Average Risk Score', 'y': 'Region'}
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    # High risk alerts
    st.subheader("⚠️ High Risk Beneficiaries - Immediate Action Required")
    high_risk_df = df[df['risk_category'] == 'High'].sort_values('risk_score', ascending=False).head(10)
    
    if len(high_risk_df) > 0:
        for idx, row in high_risk_df.iterrows():
            with st.expander(f"🚨 {row['name']} - Risk Score: {row['risk_score']}/100 ({row['region']})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Age:** {row['age_group']}")
                    st.write(f"**Gender:** {row['gender']}")
                with col2:
                    st.write(f"**Meals/Day:** {row['meals_per_day']}")
                    st.write(f"**Food Diversity:** {row['food_diversity_score']}/7")
                with col3:
                    st.write(f"**Protein:** {row['protein_intake_g']}g")
                    st.write(f"**Attendance:** {row['attendance_rate']*100:.0f}%")
    else:
        st.success("✅ No high-risk cases currently!")
    
    # Trend analysis
    st.subheader("📈 Risk Trends Over Time")
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    daily_risk = df.groupby(df['last_updated'].dt.date)['risk_score'].mean().reset_index()
    daily_risk.columns = ['date', 'avg_risk']
    
    fig_trend = px.line(
        daily_risk,
        x='date',
        y='avg_risk',
        title="Average Risk Score Over Time",
        markers=True
    )
    fig_trend.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Age group analysis
    st.subheader("👶 Risk by Age Group")
    age_risk = df.groupby(['age_group', 'risk_category']).size().unstack(fill_value=0)
    fig_age = px.bar(
        age_risk,
        barmode='stack',
        color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
    )
    st.plotly_chart(fig_age, use_container_width=True)

# ==================== TAB 2: CHATBOT ====================
with tab2:
    st.subheader("💬 Beneficiary Meal Chat Interface")
    st.markdown("*Simple interface for beneficiaries to log meals and get instant risk assessment*")
    
    # Language selector
    language = st.selectbox("Select Language", ["English", "हिंदी (Hindi)", "தமிழ் (Tamil)"], key="lang")
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input
    user_input = st.chat_input("What did you eat today? (e.g., rice, dal, vegetables)")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        response = requests.post(
            f"{API_URL}/chat",
            json={"user_message": user_input, "language": "en"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            reply = f"**Detected meals:** {', '.join(data['detected_meals']) if data['detected_meals'] else 'None'}\n\n"
            reply += f"**Food groups:** {', '.join(data['food_groups']) if data['food_groups'] else 'None'}\n\n"
            reply += f"**Diversity score:** {data['diversity_score']}/7\n\n"
            reply += f"**Suggestion:** {data['suggestion']}"
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
        
        st.rerun()

# ==================== TAB 3: RISK CHECKER ====================
with tab3:
    st.subheader("🔍 Individual Risk Assessment Tool")
    st.markdown("*Enter beneficiary details to predict nourishment risk*")
    
    with st.form("risk_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age_group = st.selectbox("Age Group", ['0-2 years', '3-5 years', '6-12 years', '13-18 years'])
            gender = st.selectbox("Gender", ['Male', 'Female'])
            region = st.selectbox("Region", df['region'].unique().tolist())
            meals = st.slider("Meals per Day", 1, 4, 3)
        
        with col2:
            diversity = st.slider("Food Diversity Score (1-7)", 1, 7, 4)
            protein = st.number_input("Protein Intake (g)", 0, 100, 35)
            calories = st.number_input("Calorie Intake (kcal)", 0, 3000, 1500)
            attendance = st.slider("Attendance Rate", 0.0, 1.0, 0.85)
        
        submitted = st.form_submit_button("🔍 Check Risk", use_container_width=True)
    
    if submitted:
        # Call API
        input_data = {
            "age_group": age_group,
            "gender": gender,
            "region": region,
            "meals_per_day": meals,
            "food_diversity_score": diversity,
            "protein_intake_g": protein,
            "calorie_intake_kcal": calories,
            "attendance_rate": attendance,
            "days_since_last_check": 0
        }
        
        with st.spinner("Analyzing..."):
            response = requests.post(f"{API_URL}/predict", json=input_data)
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Risk Assessment Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                risk_color = 'red' if result['risk_score'] > 60 else 'orange' if result['risk_score'] > 30 else 'green'
                st.markdown(f"### Risk Score")
                st.markdown(f"<h1 style='color: {risk_color};'>{result['risk_score']}/100</h1>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"### Risk Category")
                category_emoji = '🔴' if result['risk_category'] == 'High' else '🟡' if result['risk_category'] == 'Medium' else '🟢'
                st.markdown(f"<h1>{category_emoji} {result['risk_category']}</h1>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"### Confidence")
                st.markdown(f"<h1>{result['confidence']}%</h1>", unsafe_allow_html=True)
            
            # Recommendations
            st.subheader("💡 Personalized Recommendations")
            for rec in result['recommendations']:
                st.info(rec)
        else:
            st.error("Error predicting risk. Please try again.")

# Footer
st.markdown("---")
st.markdown("**NourishAI Intelligence** | Powered by Machine Learning | Built for Food Programs")