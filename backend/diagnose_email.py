"""
Email Diagnostic Script for Render
Run this to test SMTP configuration
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get from environment (Render will inject these)
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)

print("=" * 80)
print("EMAIL DIAGNOSTIC TEST - Mr Chima Portfolio Backend")
print("=" * 80)
print(f"\nConfiguration:")
print(f"  SMTP_HOST: {SMTP_HOST}")
print(f"  SMTP_PORT: {SMTP_PORT}")
print(f"  SMTP_USE_SSL: {SMTP_USE_SSL}")
print(f"  SMTP_USER: {SMTP_USER}")
print(f"  FROM_EMAIL: {FROM_EMAIL}")
print(f"  SMTP_PASSWORD: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
print("=" * 80)

# Check if credentials are set
if not SMTP_USER or not SMTP_PASSWORD:
    print("\n❌ ERROR: SMTP credentials not set in environment variables!")
    print("\nPlease set these in Render Dashboard:")
    print("  - SMTP_USER")
    print("  - SMTP_PASSWORD")
    exit(1)

# Create test email
msg = MIMEMultipart('alternative')
msg['From'] = f'Mr Chima Portfolio <{FROM_EMAIL}>'
msg['To'] = SMTP_USER  # Send to yourself
msg['Subject'] = '✅ Render SMTP Test - Success!'

html = f"""
<html>
<body style="font-family: Arial; padding: 20px;">
    <h2 style="color: #00C853;">✅ EMAIL TEST SUCCESSFUL!</h2>
    <p>If you're reading this, your SMTP configuration on Render is working correctly!</p>
    <hr>
    <p><strong>Configuration:</strong></p>
    <ul>
        <li>Host: {SMTP_HOST}</li>
        <li>Port: {SMTP_PORT}</li>
        <li>SSL/TLS: {'SSL' if SMTP_USE_SSL else 'STARTTLS'}</li>
        <li>User: {SMTP_USER}</li>
    </ul>
    <hr>
    <p>Tested from: <strong>Render Backend</strong></p>
</body>
</html>
"""

msg.attach(MIMEText(html, 'html'))

print("\n🧪 Testing SMTP Connection...")
print("-" * 80)

try:
    if SMTP_USE_SSL:
        # Port 465 - SSL
        print("1. Connecting with SSL...")
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        print("   ✓ Connected with SSL")
    else:
        # Port 587 - STARTTLS
        print("1. Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        print("   ✓ Connected")
        
        print("\n2. Starting TLS encryption...")
        server.set_debuglevel(1)  # Show detailed TLS handshake
        server.starttls()
        print("   ✓ TLS encryption started")
    
    print("\n3. Authenticating...")
    server.set_debuglevel(0)  # Turn off debug for login
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("   ✓ Authentication successful")
    
    print("\n4. Sending test email...")
    server.send_message(msg)
    print(f"   ✓ Email sent to {SMTP_USER}")
    
    server.quit()
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! SMTP IS WORKING CORRECTLY")
    print("=" * 80)
    print(f"\n📬 Check your inbox: {SMTP_USER}")
    print("(Also check spam folder)")
    print("\nYour backend should now be able to send emails!")
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 80)
    print("❌ AUTHENTICATION FAILED!")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\n🔧 POSSIBLE FIXES:")
    print("1. Check your Gmail App Password is correct")
    print("2. Make sure 2FA is enabled on your Gmail account")
    print("3. Generate a NEW App Password:")
    print("   → Go to: https://myaccount.google.com/apppasswords")
    print("   → Sign in with your Google account")
    print("   → Generate new password for 'Mail'")
    print("   → Update SMTP_PASSWORD in Render with the NEW 16-character password")
    print("\n4. Make sure you're using the App Password, NOT your regular Gmail password")
    
except smtplib.SMTPServerDisconnected as e:
    print("\n" + "=" * 80)
    print("❌ CONNECTION FAILED!")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\n🔧 POSSIBLE FIXES:")
    print("1. Check SMTP_HOST is correct: smtp.gmail.com")
    print("2. Check SMTP_PORT is correct: 587")
    print("3. Check SMTP_USE_SSL is set to: false (for port 587)")
    
except Exception as e:
    print("\n" + "=" * 80)
    print(f"❌ ERROR: {type(e).__name__}")
    print("=" * 80)
    print(f"\nError message: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    
print("\n" + "=" * 80)
print("End of diagnostic test")
print("=" * 80)
