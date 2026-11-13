# 🚀 GO LIVE CHECKLIST - Paystack Production

## ✅ BACKEND (Render Dashboard)

1. Go to: https://dashboard.render.com
2. Select your service: `mrchima-portfolio`
3. Click **Environment** tab
4. Update these variables:

```
PAYSTACK_SECRET_KEY = sk_live_YOUR_LIVE_SECRET_KEY
PAYSTACK_PUBLIC_KEY = pk_live_YOUR_LIVE_PUBLIC_KEY
```

5. Click **Save Changes** (Render will auto-redeploy)

---

## ✅ FRONTEND (hire.html)

Replace the placeholder in `hire.html` line ~598:

```javascript
key: 'pk_live_YOUR_LIVE_PUBLIC_KEY', // Replace with actual key
```

With your actual live public key:

```javascript
key: 'pk_live_xxxxxxxxxxxxx',
```

---

## ✅ WEBHOOK (Optional but Recommended)

If Paystack requires a webhook URL for live mode:

**Webhook URL:** `https://mrchima-portfolio.onrender.com/api/paystack-webhook`

**Events to subscribe to:**
- `charge.success` - Payment successful
- `charge.failed` - Payment failed

**How to set up:**
1. Go to Paystack Dashboard → Settings → Webhooks
2. Add webhook URL above
3. Copy the webhook secret
4. Add to Render environment variables:
   ```
   PAYSTACK_WEBHOOK_SECRET = whsec_xxxxxxxxxxxxx
   ```

---

## ✅ TESTING BEFORE GO-LIVE

1. **Test on staging first** if possible
2. **Use small amounts** (₦100) for first live test
3. **Verify emails are sent** after payment
4. **Check download links work**
5. **Test support button** works
6. **Monitor backend logs** on Render for any errors

---

## 🎯 WHAT HAPPENS AFTER YOU GO LIVE

- **Real charges**: All payments will be REAL money
- **Real payouts**: Money goes to your bank account
- **No test cards**: Test cards like `4084084084084081` will NOT work
- **Real emails**: Customers receive actual download links
- **Paystack fees**: Paystack will charge their standard 1.5% + ₦100 fee

---

## 🔐 SECURITY NOTES

- ✅ Never commit `.env` files to git
- ✅ Keep secret keys SECRET (never in frontend code)
- ✅ Public keys are safe in frontend (they're meant to be public)
- ✅ Backend validates all payments before sending downloads
- ✅ Download links expire after 7 days / 3 downloads

---

## 📊 MONITORING

After going live, monitor:

1. **Render Logs**: Check for payment processing errors
2. **Paystack Dashboard**: Monitor successful/failed payments
3. **Email delivery**: Check Brevo for email send status
4. **Customer support**: Watch for customer complaints about downloads

---

## 🆘 ROLLBACK (If something goes wrong)

If you need to go back to test mode:

1. Change Render env vars back to `sk_test_` and `pk_test_`
2. Change hire.html back to `pk_test_28abc456def789gh`
3. Git commit and push
4. Wait for deployment

---

## 📁 FILES THAT NEED UPDATING

1. **Render Environment Variables** (Backend)
   - `PAYSTACK_SECRET_KEY`
   - `PAYSTACK_PUBLIC_KEY`

2. **hire.html** (Frontend)
   - Line ~598: Update hardcoded public key

3. **That's it!** (index.html and source-code.html fetch the key from backend)

---

## ✨ YOU'RE READY!

Once you update these 2 things, your site will be LIVE and accepting real payments! 🎉
