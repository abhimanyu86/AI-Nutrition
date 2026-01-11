# 🚀 Google Cloud Run Deployment Guide

Complete guide to deploy NourishAI Intelligence Platform on Google Cloud Run.

---

## 📋 Prerequisites

### 1. Google Cloud Platform Account
- Create a GCP account at https://cloud.google.com
- Set up billing (Free tier available: $300 credit for 90 days)
- Create a new project or use an existing one

### 2. Install Google Cloud SDK
```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows
# Download from: https://cloud.google.com/sdk/docs/install
```

### 3. Authenticate
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 🎯 Quick Deployment (Recommended)

Deploy both backend and frontend with a single command:

```bash
# Make the script executable
chmod +x deploy-all.sh

# Deploy everything
./deploy-all.sh YOUR_PROJECT_ID us-central1
```

**That's it!** Your application will be deployed in ~5-10 minutes.

---

## 🔧 Manual Deployment (Step-by-Step)

### Step 1: Deploy Backend API

```bash
chmod +x deploy-backend.sh
./deploy-backend.sh YOUR_PROJECT_ID us-central1
```

**What this does:**
- Builds FastAPI backend container
- Deploys to Cloud Run with 2GB memory, 2 vCPU
- Enables auto-scaling (0 to 10 instances)
- Returns backend URL (save this for next step)

### Step 2: Deploy Frontend Dashboard

```bash
chmod +x deploy-frontend.sh
./deploy-frontend.sh YOUR_PROJECT_ID us-central1 BACKEND_URL
```

**Replace `BACKEND_URL`** with the URL from Step 1.

**What this does:**
- Builds Streamlit dashboard container
- Deploys to Cloud Run with environment variable for backend
- Enables auto-scaling
- Returns frontend URL (this is your app!)

---

## 🌍 Available Regions

Choose a region close to your users:

| Region | Location | Code |
|--------|----------|------|
| US Central | Iowa | `us-central1` |
| US East | South Carolina | `us-east1` |
| Europe West | Belgium | `europe-west1` |
| Asia South | Mumbai | `asia-south1` |
| Asia Southeast | Singapore | `asia-southeast1` |

Example:
```bash
./deploy-all.sh my-project asia-south1  # Deploy to Mumbai
```

---

## 🧪 Testing Your Deployment

### Test Backend API
```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe nourishai-backend --region us-central1 --format 'value(status.url)')

# Test health check
curl $BACKEND_URL

# Test prediction endpoint
curl -X POST $BACKEND_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age_group": "3-5 years",
    "gender": "Female",
    "region": "Maharashtra",
    "meals_per_day": 2,
    "food_diversity_score": 3,
    "protein_intake_g": 25.0,
    "calorie_intake_kcal": 1200.0,
    "attendance_rate": 0.75,
    "days_since_last_check": 15,
    "language": "en"
  }'
```

### Test Frontend Dashboard
```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe nourishai-frontend --region us-central1 --format 'value(status.url)')

# Open in browser
open $FRONTEND_URL  # macOS
xdg-open $FRONTEND_URL  # Linux
start $FRONTEND_URL  # Windows
```

---

## 📊 Monitoring & Management

### View Logs
```bash
# Backend logs
gcloud run services logs read nourishai-backend --region us-central1 --limit 50

# Frontend logs
gcloud run services logs read nourishai-frontend --region us-central1 --limit 50

# Follow logs in real-time
gcloud run services logs tail nourishai-backend --region us-central1
```

### Check Service Status
```bash
# List all services
gcloud run services list --region us-central1

# Describe specific service
gcloud run services describe nourishai-backend --region us-central1
```

### View Service URLs
```bash
# Get URLs
gcloud run services list --region us-central1 --format="table(service,status.url)"
```

---

## 🔄 Updating Your Deployment

### Update Backend
```bash
# Make changes to backend.py
# Then redeploy
./deploy-backend.sh YOUR_PROJECT_ID us-central1
```

### Update Frontend
```bash
# Make changes to dashboard.py
# Get current backend URL
BACKEND_URL=$(gcloud run services describe nourishai-backend --region us-central1 --format 'value(status.url)')

# Redeploy
./deploy-frontend.sh YOUR_PROJECT_ID us-central1 $BACKEND_URL
```

### Update Both
```bash
./deploy-all.sh YOUR_PROJECT_ID us-central1
```

---

## 🔒 Security Configuration

### Enable Authentication (Optional)

For production, you may want to require authentication:

```bash
# Remove public access
gcloud run services remove-iam-policy-binding nourishai-frontend \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region us-central1

# Add specific users
gcloud run services add-iam-policy-binding nourishai-frontend \
  --member="user:email@example.com" \
  --role="roles/run.invoker" \
  --region us-central1
```

### Set Environment Variables

```bash
# Update backend with custom environment variables
gcloud run services update nourishai-backend \
  --set-env-vars "CUSTOM_VAR=value" \
  --region us-central1

# Update frontend API URL
gcloud run services update nourishai-frontend \
  --set-env-vars "API_URL=https://your-backend-url.run.app" \
  --region us-central1
```

---

## 💰 Cost Optimization

### Cloud Run Pricing (as of 2024)
- **Free Tier:** 2M requests/month, 360,000 GB-seconds, 180,000 vCPU-seconds
- **After Free Tier:**
  - $0.00002400 per request
  - $0.00000250 per GB-second
  - $0.00002400 per vCPU-second

### Cost-Saving Tips

1. **Auto-scaling to Zero**
   - Services automatically scale to 0 when not in use
   - No charges when idle

2. **Reduce Resources for Demo**
   ```bash
   gcloud run services update nourishai-backend \
     --memory 1Gi \
     --cpu 1 \
     --region us-central1
   ```

3. **Set Request Timeout**
   ```bash
   gcloud run services update nourishai-backend \
     --timeout 60 \
     --region us-central1
   ```

4. **Limit Max Instances**
   ```bash
   gcloud run services update nourishai-backend \
     --max-instances 5 \
     --region us-central1
   ```

---

## 🗑️ Cleanup / Delete Services

### Delete Individual Service
```bash
gcloud run services delete nourishai-backend --region us-central1
gcloud run services delete nourishai-frontend --region us-central1
```

### Delete All Resources
```bash
# Delete both services
gcloud run services delete nourishai-backend nourishai-frontend --region us-central1 --quiet

# Delete container images
gcloud container images delete gcr.io/YOUR_PROJECT_ID/nourishai-backend --quiet
gcloud container images delete gcr.io/YOUR_PROJECT_ID/nourishai-frontend --quiet
```

---

## 🐛 Troubleshooting

### Issue: Deployment Fails

**Check build logs:**
```bash
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

### Issue: Service Not Responding

**Check service logs:**
```bash
gcloud run services logs read nourishai-backend --region us-central1 --limit 100
```

### Issue: Frontend Can't Connect to Backend

**Verify environment variable:**
```bash
gcloud run services describe nourishai-frontend --region us-central1 --format="get(spec.template.spec.containers[0].env)"
```

**Update API URL:**
```bash
BACKEND_URL=$(gcloud run services describe nourishai-backend --region us-central1 --format 'value(status.url)')
gcloud run services update nourishai-frontend \
  --set-env-vars "API_URL=$BACKEND_URL" \
  --region us-central1
```

### Issue: Out of Memory

**Increase memory:**
```bash
gcloud run services update nourishai-backend \
  --memory 4Gi \
  --region us-central1
```

### Issue: Cold Start Delays

**Set minimum instances:**
```bash
gcloud run services update nourishai-backend \
  --min-instances 1 \
  --region us-central1
```
*Note: This will incur costs even when idle*

---

## 📱 Custom Domain Setup (Optional)

### 1. Verify Domain Ownership
```bash
gcloud domains verify EXAMPLE.COM
```

### 2. Map Domain to Service
```bash
gcloud run domain-mappings create \
  --service nourishai-frontend \
  --domain app.example.com \
  --region us-central1
```

### 3. Update DNS Records
Add the DNS records shown in the output to your domain provider.

---

## 🔗 Useful Links

- **Cloud Run Documentation:** https://cloud.google.com/run/docs
- **Cloud Run Pricing:** https://cloud.google.com/run/pricing
- **Cloud Console:** https://console.cloud.google.com/run
- **GCP Free Tier:** https://cloud.google.com/free

---

## 📞 Support

### View Service Details
```bash
gcloud run services describe nourishai-backend --region us-central1
```

### Get Help
```bash
gcloud run deploy --help
gcloud run services --help
```

---

## ✅ Deployment Checklist

- [ ] GCP account created
- [ ] gcloud CLI installed
- [ ] Project created in GCP
- [ ] Billing enabled
- [ ] Authenticated with `gcloud auth login`
- [ ] Project ID noted
- [ ] Region selected
- [ ] Deployment scripts made executable
- [ ] Backend deployed successfully
- [ ] Backend URL noted
- [ ] Frontend deployed with correct backend URL
- [ ] Both services tested
- [ ] URLs shared with stakeholders

---

**Built with ❤️ for social impact and enterprise AI**
