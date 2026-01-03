# 🚀 Quick Start Guide - NourishAI

## ⚡ Get Running in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend API
```bash
python backend.py
```
✅ API runs on **http://localhost:8000**

### Step 3: Start the Dashboard (New Terminal)
```bash
streamlit run dashboard.py
```
✅ Dashboard opens at **http://localhost:8501**

---

## 🎯 What You Can Do

### 1. Beneficiary Chat Interface (Tab 2)
1. Select your language (13 languages available)
2. Click 🎤 microphone button OR type your message
3. Describe what you ate: "I had rice, dal, and vegetables"
4. Get instant feedback on dietary diversity

### 2. Risk Assessment (Tab 3)
1. Select language for recommendations
2. Fill in beneficiary details (age, gender, meals, etc.)
3. Optionally use 🎤 voice notes
4. Get risk prediction with personalized recommendations in your language

### 3. Dashboard (Tab 1)
- View total beneficiaries
- See high-risk alerts
- Analyze regional patterns
- Monitor trends over time

---

## 🌍 Supported Languages

English • Hindi • Tamil • Telugu • Kannada • Malayalam • Marathi • Bengali • Gujarati • Punjabi • Odia • Assamese • Urdu

---

## 🎤 Voice Input Tips

- **Best browsers:** Chrome, Edge
- **Enable microphone** when prompted
- **Speak clearly** in your selected language
- **Click stop** when done speaking
- **Copy the text** from transcript box and submit

---

## 📊 Sample Data

The system comes with:
- ✅ 5,000 beneficiaries
- ✅ 20 Indian regions
- ✅ Based on real NFHS-5 health survey data
- ✅ 91% accurate ML models

---

## 🔧 Troubleshooting

### API not responding?
```bash
# Check if backend is running
curl http://localhost:8000/
```

### Voice input not working?
- Use Chrome or Edge browser
- Check microphone permissions
- Ensure HTTPS (for deployment)

### Dashboard not loading?
```bash
# Reinstall streamlit
pip install --upgrade streamlit
```

---

## 🚀 Next Steps

1. **Test the chat** - Try asking in Hindi: "आज मैंने रोटी खाई"
2. **Check risk assessment** - Test with different age groups
3. **Explore dashboard** - View analytics and insights
4. **Read README.md** - Full documentation

---

## 📞 Quick API Test

```bash
# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age_group": "3-5 years",
    "gender": "Female",
    "region": "Maharashtra",
    "meals_per_day": 2,
    "food_diversity_score": 3,
    "protein_intake_g": 25,
    "calorie_intake_kcal": 1200,
    "attendance_rate": 0.75,
    "language": "hi"
  }'
```

---

**🎉 You're all set! Start exploring NourishAI.**
