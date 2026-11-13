# Email Setup Instructions for Mr Chima Portfolio Backend

## Problem
Users are not receiving emails after:
- Making support payments
- Purchasing source code

## Root Cause
The backend at `https://mrchima-portfolio.onrender.com` is missing SMTP email configuration in the environment variables.

## Solution: Configure Environment Variables on Render

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Enable **2-Step Verification** if not already enabled
4. After 2-Step is enabled, go back to Security
5. Search for **App passwords** or scroll down to find it
6. Click **App passwords**
7. Select **Mail** and **Other (Custom name)**
8. Name it: `Mr Chima Portfolio Backend`
9. Click **Generate**
10. **COPY THE 16-CHARACTER PASSWORD** (example: `abcd efgh ijkl mnop`)
11. **Keep this password safe** - you'll need it in Step 2

### Step 2: Configure Render Environment Variables

1. Go to https://dashboard.render.com/
2. Find your **mrchima-portfolio** backend service
3. Click on it to open
4. Click **Environment** in the left sidebar
5. Add these environment variables (click **Add Environment Variable** for each):

#### Required Variables:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USER=abonejoseph@gmail.com
SMTP_PASSWORD=<paste the 16-char app password from Step 1>
FROM_EMAIL=abonejoseph@gmail.com
FROM_NAME=Abone Chima (Mr Chima)
```

#### Your Paystack Keys (you should already have these):

```
PAYSTACK_SECRET_KEY=sk_live_YOUR_SECRET_KEY
PAYSTACK_PUBLIC_KEY=pk_live_YOUR_PUBLIC_KEY
```

#### Domain:

```
DOMAIN=https://mrchima.dev
```

#### Security (generate a random key):

```
SECRET_KEY=<generate random 64-character hex string>
TOKEN_EXPIRY_HOURS=168
MAX_DOWNLOADS_PER_TOKEN=3
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=3600
```

To generate SECRET_KEY, run this in PowerShell:
```powershell
-join ((0..63) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
```

### Step 3: Save and Deploy

1. Click **Save Changes** at the bottom
2. Render will automatically redeploy your backend
3. Wait 2-3 minutes for deployment to complete

### Step 4: Test Email

After deployment:
1. Go to https://mrchima.dev
2. Try making a test support payment (₦100)
3. Check your email (both customer email and abonejoseph@gmail.com)

## Email Flow

### Support Payments:
1. Customer pays via Paystack
2. Frontend calls `/api/verify-support`
3. Backend verifies payment with Paystack
4. Backend sends TWO emails:
   - **Customer**: Clean iOS-style thank you email
   - **Admin (abonejoseph@gmail.com)**: Notification with amount and customer details

### Source Code Purchase:
1. Customer pays via Paystack
2. Frontend calls `/api/verify-payment`
3. Backend verifies payment
4. Backend generates secure download token
5. Backend sends email with download link
6. Customer can download (up to 3 times, expires in 7 days)

## Troubleshooting

### Emails still not sending?

1. **Check Render logs:**
   - Go to your service on Render
   - Click **Logs** tab
   - Look for errors like:
     - `Email error: ...`
     - `SMTPAuthenticationError`
     - `Connection refused`

2. **Common issues:**
   - **Wrong App Password**: Make sure you copied it correctly (no spaces)
   - **2-Step Verification not enabled**: Gmail requires this for App Passwords
   - **SMTP blocked**: Some networks block port 587
   - **Gmail security**: Check https://myaccount.google.com/security for any blocked sign-in attempts

3. **Test SMTP connection:**
   Add this to backend and check logs:
   ```python
   print(f"SMTP Config: {SMTP_HOST}:{SMTP_PORT}")
   print(f"SMTP User: {SMTP_USER}")
   print(f"SMTP Password set: {bool(SMTP_PASSWORD)}")
   ```

### Environment variables not loading?

- Make sure they're saved on Render
- Restart the service manually if needed
- Check for typos in variable names (case-sensitive!)

## Alternative: Use SendGrid (If Gmail doesn't work)

If Gmail App Passwords don't work, you can use SendGrid:

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create an API key
3. Update environment variables:
   ```
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USE_SSL=false
   SMTP_USER=apikey
   SMTP_PASSWORD=<your SendGrid API key>
   FROM_EMAIL=abonejoseph@gmail.com
   ```

## Security Notes

- ✅ App Passwords are safer than your real Gmail password
- ✅ You can revoke App Passwords anytime from Google Account settings
- ✅ Never commit .env file to git (it's in .gitignore)
- ✅ Backend uses secure token system with IP binding for downloads

## Contact

If you still have issues after following these steps, check:
1. Render deployment logs
2. Browser console for frontend errors
3. Test with a small support amount first (₦100)

---

**Status**: Ready to configure ✅
**Time needed**: 10-15 minutes
**Difficulty**: Easy (just copy-paste environment variables)
