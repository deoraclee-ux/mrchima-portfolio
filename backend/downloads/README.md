# Downloads Folder

## 📦 Place Your Product Files Here

This folder contains all digital products available for purchase.

### Current Products:

1. **Oracle Weather App**
   - File: `Oracle-Weather-App.zip`
   - Price: ₦8,000
   - Status: ⚠️ Add file here

2. **Mr Chima AI Agent**
   - File: `mr-chima-ai-agent.zip`
   - Price: ₦15,000
   - Status: ⚠️ Add file here

3. **WhatsApp Bot Source Code**
   - File: `whatsapp-bot-source.zip`
   - Price: ₦20,000
   - Status: ⚠️ Add file here

---

## 🔒 Security Notes

All files in this folder are protected by:
- ✅ Payment verification (Paystack)
- ✅ IP address binding
- ✅ Browser binding
- ✅ One-time use tokens
- ✅ Time-based expiration
- ✅ Rate limiting
- ✅ Complete audit logging

**Customers can ONLY download after:**
1. Successful payment via Paystack
2. From the SAME device they paid from
3. Using the SAME browser they paid with
4. Within 7 days of purchase
5. Maximum 3 downloads per purchase

---

## 📝 Adding New Products

### Step 1: Add ZIP File
Place your product ZIP here:
```
downloads/your-product.zip
```

### Step 2: Update server.py
Add to PRODUCTS dictionary:
```python
PRODUCTS = {
    'your-product': {
        'name': 'Your Product Name',
        'filename': 'your-product.zip',
        'filepath': 'downloads/your-product.zip',
        'price': 10000  # Price in kobo (₦100.00)
    }
}
```

### Step 3: Test
```bash
# Check file exists:
ls downloads/your-product.zip

# Restart backend (auto-reloads)
# Test with Paystack test card
```

---

## ⚠️ Important

**DO NOT:**
- ❌ Share files from this folder publicly
- ❌ Put sensitive data in filenames
- ❌ Store unzipped source code here
- ❌ Delete files while downloads are active

**DO:**
- ✅ Keep files as ZIP archives
- ✅ Use descriptive filenames
- ✅ Backup this folder regularly
- ✅ Check file sizes are correct
- ✅ Scan for viruses before uploading

---

## 🔍 Verification

Before going live, verify:
```bash
# 1. Check all files exist
ls *.zip

# 2. Check file sizes
Get-ChildItem *.zip | Select-Object Name, Length

# 3. Test ZIP integrity
Expand-Archive Oracle-Weather-App.zip -DestinationPath test -Force
```

---

## 📊 File Size Recommendations

- **Small projects**: < 10 MB
- **Medium projects**: 10-50 MB
- **Large projects**: 50-100 MB
- **Maximum**: 500 MB (adjust if needed)

For files > 100 MB:
- Consider using Google Drive + secure tokens
- Or split into multiple smaller files
- Or use CDN for delivery

---

## 🎯 Current Status

| Product | File | Status |
|---------|------|--------|
| Oracle Weather App | Oracle-Weather-App.zip | ⚠️ Missing |
| Mr Chima AI Agent | mr-chima-ai-agent.zip | ⚠️ Missing |
| WhatsApp Bot | whatsapp-bot-source.zip | ⚠️ Missing |

**Action Required**: Add your ZIP files to start selling! 🚀
