# Brevo (Sendinblue) Email Setup for Render

**Why Brevo?** Render blocks SMTP ports (587, 465) to prevent spam. Brevo uses HTTP API instead, which works perfectly on Render.

## Step 1: Create Brevo Account

1. Go to: **https://www.brevo.com/** (formerly Sendinblue)
2. Click **"Sign up free"**
3. Sign up with your email (use **abonejoseph@gmail.com**)
4. Complete email verification
5. Fill in company details (can skip most optional fields)

**Free Tier:** 300 emails/day forever - perfect for your portfolio! 🎉

## Step 2: Verify Sender Email (Required!)

Brevo requires sender verification to prevent spam:

1. After signup, you'll be prompted to verify your email
2. Or go to: **Settings** → **Senders & IP**
3. Click **"Add a sender"**
4. Fill in:
   - **Email:** `abonejoseph@gmail.com`
   - **Name:** `Mr Chima Portfolio` or `Abone Chima`
5. Click **"Add"**
6. **Check your email** (abonejoseph@gmail.com)
7. Click the verification link in the email from Brevo
8. ✅ Done! You can now send from `abonejoseph@gmail.com`

## Step 3: Create API Key

1. In Brevo dashboard, click your name (top-right) → **"SMTP & API"**
   - Or go directly to: **https://app.brevo.com/settings/keys/api**
2. Under **"API Keys"** section
3. Click **"Generate a new API key"** or **"Create a new API key"**
4. Settings:
   - **Name:** `Render Backend` or `Portfolio Backend`
5. Click **"Generate"**
6. **Copy the API key** (looks like: `xkeysib-xxxxxxxxxxxxx...`)
   - ⚠️ **Important:** Save it now! You can't see it again!

## Step 4: Configure Render

1. Go to your **Render Dashboard**
2. Select your backend service
3. Click **"Environment"** tab
4. Add new environment variable:
   - **Key:** `BREVO_API_KEY`
   - **Value:** Paste the API key from Step 3
5. Update these variables:
   - **Key:** `FROM_EMAIL`
   - **Value:** `abonejoseph@gmail.com` (must match verified sender)
   
   - **Key:** `FROM_NAME`
   - **Value:** `Mr Chima Portfolio` or `Abone Chima`
6. Click **"Save Changes"**

Render will automatically redeploy with Brevo enabled! ⚡

## Step 5: Test It!

After Render redeploys (takes ~2 minutes):

1. Try a test payment on your site
2. Check the **Render logs** - you should see:
   ```
   📧 Email Configuration:
      Brevo API: ✓ Configured
      From: Mr Chima Portfolio <abonejoseph@gmail.com>
      ℹ️  Using Brevo API (SMTP blocked on Render)
   
   📧 Sending email via Brevo API to: customer@example.com
      Subject: Your WhatsApp Bot Source Code Download Link
   ✓ Email sent successfully via Brevo to customer@example.com!
      Message ID: <some-id>
   ```
3. **Check your email inbox!** 📬

## Environment Variables Summary

After setup, your Render environment should have:

```env
BREVO_API_KEY = xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL = abonejoseph@gmail.com
FROM_NAME = Mr Chima Portfolio
```

You can **remove** the old SMTP variables (no longer needed):
- ~~SMTP_HOST~~
- ~~SMTP_PORT~~
- ~~SMTP_USER~~
- ~~SMTP_PASSWORD~~
- ~~SMTP_USE_SSL~~

## Monitoring Emails

Track your email sends in Brevo:

1. Go to **Statistics** → **Email** in Brevo dashboard
2. See:
   - Emails sent
   - Delivery rate
   - Opens/clicks (if tracking enabled)
3. Check **Logs** to see individual email details

## Troubleshooting

### ❌ "Account not confirmed" error
- Make sure you clicked the verification link in your email
- Check spam folder for Brevo verification email

### ❌ "Unauthorized" or 401 error
- Check API key is correct (no extra spaces)
- Make sure you copied the full API key
- Verify API key is still active in Brevo dashboard

### ❌ "Sender email not verified"
- `FROM_EMAIL` must match the verified sender exactly
- Go to Settings → Senders & IP and verify your email

### ❌ Still not working?
- Check **Render logs** for detailed error messages
- Verify Brevo API key is active in Brevo dashboard
- Make sure you're under the 300 emails/day limit
- Check Brevo account status (suspended accounts can't send)

## Rate Limits

**Free Tier:**
- 300 emails/day
- Unlimited contacts
- Email support

If you need more, paid plans start at $25/month for 20,000 emails/month.

## Benefits of Brevo

✅ **Generous free tier** (300 vs SendGrid's 100)  
✅ **Better deliverability** - high inbox rate  
✅ **Easy setup** - no domain verification needed  
✅ **Great dashboard** - track all email stats  
✅ **Reliable** - used by 500,000+ businesses  

## Support

- Brevo Docs: https://developers.brevo.com/
- Brevo Support: https://help.brevo.com/
- API Reference: https://developers.brevo.com/reference/sendtransacemail

---

**That's it!** Your emails will now work reliably on Render using Brevo's HTTP API. 🚀📧

No more "Network unreachable" errors! ✨
