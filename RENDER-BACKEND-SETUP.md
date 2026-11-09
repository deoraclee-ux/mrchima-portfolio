# 🚀 Deploy Backend to Render - Quick Guide

## Your Frontend is LIVE! ✅
**URL**: https://mrchima-portfolio.vercel.app/

Now let's deploy the backend and connect everything!

---

## Step 1: Deploy Backend to Render (5 minutes)

### 1.1 Go to Render
👉 **https://dashboard.render.com/**
- Sign up/Sign in with GitHub (FREE)

### 1.2 Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. Connect GitHub if needed
4. Select repository: **mrchima-portfolio**
5. Click **"Connect"**

### 1.3 Configure Service

Fill in these **EXACT** settings:

```
Name: mrchima-backend
Region: Frankfurt (or Singapore - closest to Nigeria)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
Plan: Free
```

⚠️ **IMPORTANT**: Root Directory MUST be `backend`

### 1.4 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these **ONE BY ONE**:

```
PAYSTACK_SECRET_KEY=sk_test_68e51663a6b12e15da224132d05ede5655dbc593
PAYSTACK_PUBLIC_KEY=pk_test_fea0881e71919f07692e168cd3e83f843d3df569
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USER=abonejoseph@gmail.com
SMTP_PASSWORD=hbjhigmsgplzqiap
FROM_EMAIL=noreply@mrchima.dev
FROM_NAME=Abone Chima (Mr Chima)
DOMAIN=https://mrchima-portfolio.vercel.app
SECRET_KEY=mrchima_super_secret_key_change_in_production_2024
TOKEN_EXPIRY_HOURS=168
MAX_DOWNLOADS_PER_TOKEN=3
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=3600
```

### 1.5 Create Service
1. Scroll down
2. Click **"Create Web Service"**
3. Wait 3-5 minutes for deployment
4. You'll get a URL like: `https://mrchima-backend.onrender.com`
5. **COPY THIS URL!**

---

## Step 2: Connect Frontend to Backend (2 minutes)

Once your backend is deployed, you'll need to update your frontend.

### 2.1 Your Backend URL
After Render finishes deploying, you'll have something like:
```
https://mrchima-backend-xxxx.onrender.com
```

### 2.2 Update Frontend
In your `index.html`, find this line:
```javascript
const BACKEND_URL = 'http://localhost:8000'
```

Change it to:
```javascript
const BACKEND_URL = 'https://mrchima-backend-xxxx.onrender.com'
```
(Use your actual Render URL)

### 2.3 Push to GitHub
```powershell
cd "C:\Users\1040 G7\Documents\Cloned portfolio\mrchima-portfolio-clean"
git add index.html
git commit -m "Connect to Render backend"
git push origin main
```

Vercel will auto-deploy in 1 minute!

---

## Step 3: Test Everything! ✅

### 3.1 Visit Your Site
👉 https://mrchima-portfolio.vercel.app/

### 3.2 Test Payment Flow
1. Click **"Get the code"** on Telegram bot
2. Enter your email
3. Complete test payment (use test card)
4. Check your email for download link
5. Click link → Should download file!

### 3.3 Test Contact Form
1. Scroll to contact section
2. Fill in name, email, message
3. Click "Send message"
4. Should see iOS success animation
5. Check email (abonejoseph@gmail.com)

---

## 🎉 You're LIVE!

Your portfolio is now:
- ✅ Frontend: https://mrchima-portfolio.vercel.app/
- ✅ Backend: https://mrchima-backend-xxxx.onrender.com
- ✅ Payments working (Paystack)
- ✅ Downloads secured (10-layer security)
- ✅ Emails sending (Gmail SMTP)
- ✅ 100% FREE hosting!

---

## ⚠️ Important Notes

### Free Tier Behavior
- **Backend spins down** after 15 min of no activity
- **First request** takes ~30 seconds to wake up
- **After wake up**: Fast for 15 minutes
- Perfect for portfolio! Not a problem.

### Security
- Never commit `.env` to GitHub ✅
- Environment variables are on Render (secure) ✅
- Download links are IP-bound ✅
- Payments verified with Paystack ✅

### Maintenance
1. Make changes locally
2. Push to GitHub
3. Vercel/Render auto-deploy!

---

## 🐛 Troubleshooting

### Backend won't start?
- Check Render logs (in dashboard)
- Verify all environment variables
- Make sure Root Directory is `backend`

### Frontend not connecting?
- Check BACKEND_URL in index.html
- Check CORS in backend
- Verify backend is running (visit the URL)

### Payments not working?
- Check Paystack keys are correct
- Check backend logs for errors
- Verify DOMAIN in backend env vars

### Emails not sending?
- Check Gmail app password
- Verify SMTP settings
- Check backend logs

---

## 📞 Need Help?

If something's not working:
1. Check Render logs (Backend)
2. Check Vercel logs (Frontend)
3. Check browser console (F12)
4. Verify all environment variables

---

## 🎯 Next Steps (Optional)

### Custom Domain
1. Buy domain (e.g., mrchima.dev)
2. Add to Vercel: Settings → Domains
3. Update DNS records
4. Free SSL automatic!

### Upgrade Later
- Starter: $7/month (no spin down)
- Pro: $25/month (more resources)

But FREE is perfect for now! 🎉
