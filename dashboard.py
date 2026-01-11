# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import streamlit.components.v1 as components
import os

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

# API endpoint - can be set via environment variable for Cloud Run
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी (Hindi)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'ml': 'മലയാളം (Malayalam)',
    'mr': 'मराठी (Marathi)',
    'bn': 'বাংলা (Bengali)',
    'gu': 'ગુજરાતી (Gujarati)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)',
    'or': 'ଓଡ଼ିଆ (Odia)',
    'as': 'অসমীয়া (Assamese)',
    'ur': 'اردو (Urdu)'
}

# Language code mapping for Web Speech API
SPEECH_LANG_CODES = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'mr': 'mr-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'pa': 'pa-IN',
    'or': 'or-IN',
    'as': 'as-IN',
    'ur': 'ur-PK'
}

def voice_input_component(language_code='en-IN', placeholder="Speak...", key="voice"):
    """Create a voice input component using Web Speech API"""
    html_code = f"""
    <div style="padding: 10px; background: #f0f2f6; border-radius: 5px; margin: 10px 0;">
        <button id="voiceBtn_{key}" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            🎤 Start Voice Input
        </button>
        <p id="transcript_{key}" style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px; min-height: 40px;">
            {placeholder}
        </p>
        <p id="status_{key}" style="font-size: 12px; color: #666; margin-top: 5px;"></p>
    </div>

    <script>
    (function() {{
        const button = document.getElementById('voiceBtn_{key}');
        const transcript = document.getElementById('transcript_{key}');
        const status = document.getElementById('status_{key}');

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.textContent = '⚠️ Speech recognition not supported in this browser';
            button.disabled = true;
            return;
        }}

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.lang = '{language_code}';
        recognition.continuous = false;
        recognition.interimResults = false;

        let isListening = false;

        button.addEventListener('click', () => {{
            if (isListening) {{
                recognition.stop();
                isListening = false;
                button.textContent = '🎤 Start Voice Input';
                button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            }} else {{
                recognition.start();
                isListening = true;
                button.textContent = '🔴 Listening...';
                button.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                status.textContent = 'Listening... Speak now';
            }}
        }});

        recognition.onresult = (event) => {{
            const text = event.results[0][0].transcript;
            transcript.textContent = text;
            status.textContent = '✅ Speech recognized';

            // Send to Streamlit using custom event
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: text,
                key: '{key}'
            }}, '*');
        }};

        recognition.onerror = (event) => {{
            status.textContent = '❌ Error: ' + event.error;
            isListening = false;
            button.textContent = '🎤 Start Voice Input';
            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }};

        recognition.onend = () => {{
            isListening = false;
            button.textContent = '🎤 Start Voice Input';
            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }};
    }})();
    </script>
    """
    return components.html(html_code, height=200)

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
    st.markdown("**Supports 13 languages with voice input!**")

    # Language selector
    col_lang, col_info = st.columns([1, 2])
    with col_lang:
        selected_lang_display = st.selectbox(
            "🌍 Select Language / भाषा चुनें",
            list(LANGUAGES.values()),
            key="lang_chat"
        )
        # Get language code from display name
        selected_lang = [k for k, v in LANGUAGES.items() if v == selected_lang_display][0]

    with col_info:
        st.info(f"📢 Selected: {selected_lang_display} | Voice input enabled")
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Voice input section
    st.markdown("### 🎤 Voice Input or Type Below")
    st.markdown("Click the microphone button to speak, or type your message in your selected language")

    # Create tabs for voice and text input
    input_tab1, input_tab2 = st.tabs(["🎤 Voice Input", "⌨️ Text Input"])

    user_input = None

    with input_tab1:
        st.markdown(f"**Speak in {selected_lang_display}**")
        voice_input_component(
            language_code=SPEECH_LANG_CODES.get(selected_lang, 'en-IN'),
            placeholder=f"Speak your meal in {selected_lang_display}...",
            key="chat_voice"
        )
        # Note: Voice input requires manual copy for now due to Streamlit limitations
        voice_text = st.text_input(
            "Copy voice text here (from above) or type:",
            key="voice_text_chat",
            placeholder="Paste or type your meal here..."
        )
        if st.button("Submit Voice/Text", key="submit_voice_chat"):
            user_input = voice_text

    with input_tab2:
        text_input = st.text_area(
            f"What did you eat today? (Type in {selected_lang_display})",
            key="text_input_chat",
            placeholder="Example: आज मैंने रोटी, दाल और सब्जी खाई (Hindi)\nOR rice, dal, vegetables (English)"
        )
        if st.button("Send Message", key="submit_text_chat"):
            user_input = text_input

    # Display chat history
    st.markdown("---")
    st.markdown("### 💬 Chat History")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Process input
    if user_input and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get response from API
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"user_message": user_input, "language": selected_lang}
                )

                if response.status_code == 200:
                    data = response.json()

                    reply = f"**{data.get('message', 'Detected meals')}**\n\n"
                    if data['detected_meals']:
                        reply += f"**Detected meals:** {', '.join(data['detected_meals'])}\n\n"
                    if data['food_groups']:
                        reply += f"**Food groups:** {', '.join(data['food_groups'])}\n\n"
                    reply += f"**Diversity score:** {data['diversity_score']}/7\n\n"
                    reply += f"💡 **{data.get('suggestion', 'Keep up the good work!')}**"

                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error("Error connecting to API. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

        st.rerun()

# ==================== TAB 3: RISK CHECKER ====================
with tab3:
    st.subheader("🔍 Individual Risk Assessment Tool")
    st.markdown("*Enter beneficiary details to predict nourishment risk*")
    st.markdown("**Supports 13 languages with voice input!**")

    # Language selector for Risk Checker
    col_lang_risk, col_info_risk = st.columns([1, 2])
    with col_lang_risk:
        selected_lang_risk_display = st.selectbox(
            "🌍 Select Language / भाषा चुनें",
            list(LANGUAGES.values()),
            key="lang_risk"
        )
        # Get language code from display name
        selected_lang_risk = [k for k, v in LANGUAGES.items() if v == selected_lang_risk_display][0]

    with col_info_risk:
        st.info(f"📢 Selected: {selected_lang_risk_display} | Voice input enabled for notes")

    st.markdown("---")

    with st.form("risk_form"):
        col1, col2 = st.columns(2)

        with col1:
            age_group = st.selectbox("Age Group", ['0-2 years', '3-5 years', '6-12 years', '13-18 years'])
            gender = st.selectbox("Gender", ['Male', 'Female'])
            region = st.selectbox("Region", sorted(df['region'].unique().tolist()))
            meals = st.slider("Meals per Day", 1, 4, 3)

        with col2:
            diversity = st.slider("Food Diversity Score (1-7)", 1, 7, 4)
            protein = st.number_input("Protein Intake (g)", 0, 100, 35)
            calories = st.number_input("Calorie Intake (kcal)", 0, 3000, 1500)
            attendance = st.slider("Attendance Rate", 0.0, 1.0, 0.85)

        submitted = st.form_submit_button("🔍 Check Risk", use_container_width=True)
    
    # Voice input for additional notes (outside form)
    st.markdown("### 🎤 Optional: Add Voice Notes")
    st.markdown("Use voice to describe additional details about the beneficiary")
    voice_input_component(
        language_code=SPEECH_LANG_CODES.get(selected_lang_risk, 'en-IN'),
        placeholder=f"Speak additional notes in {selected_lang_risk_display}...",
        key="risk_voice"
    )

    if submitted:
        # Call API with language support
        input_data = {
            "age_group": age_group,
            "gender": gender,
            "region": region,
            "meals_per_day": meals,
            "food_diversity_score": diversity,
            "protein_intake_g": protein,
            "calorie_intake_kcal": calories,
            "attendance_rate": attendance,
            "days_since_last_check": 0,
            "language": selected_lang_risk
        }

        with st.spinner("Analyzing..."):
            try:
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

                    # Recommendations (translated)
                    st.subheader(f"💡 Personalized Recommendations ({selected_lang_risk_display})")
                    for rec in result['recommendations']:
                        st.info(rec)

                    st.success(f"✅ Results displayed in {selected_lang_risk_display}")
                else:
                    st.error("Error predicting risk. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}\n\nMake sure the API server is running on {API_URL}")

# Footer
st.markdown("---")
st.markdown("**NourishAI Intelligence** | Powered by Machine Learning | Built for Food Programs")