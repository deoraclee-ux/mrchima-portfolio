"""Quick test to verify SMTP email works"""
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'true').lower() == 'true'
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@mrchima.dev')

print("=" * 60)
print("SMTP Email Test")
print("=" * 60)
print(f"Host: {SMTP_HOST}")
print(f"Port: {SMTP_PORT}")
print(f"SSL: {SMTP_USE_SSL}")
print(f"User: {SMTP_USER}")
print(f"From: {FROM_EMAIL}")
print("=" * 60)

try:
    # Create test message
    msg = MIMEMultipart('alternative')
    msg['From'] = f'Abone Chima <{FROM_EMAIL}>'
    msg['To'] = SMTP_USER  # Send to yourself
    msg['Subject'] = '✅ Test Email from Mr Chima Portfolio'
    
    html = """
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h2 style="color: #007ACC;">✅ Email Test Successful!</h2>
        <p>If you received this, SMTP is working correctly!</p>
        <p>From: Mr Chima Portfolio Backend</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    print("\n1. Connecting to SMTP server...")
    if SMTP_USE_SSL:
        # Port 465 - SSL
        import smtplib
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        print("   ✓ Connected with SSL")
    else:
        # Port 587 - TLS
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.starttls()
        print("   ✓ Connected with TLS")
    
    print("\n2. Logging in...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("   ✓ Login successful")
    
    print("\n3. Sending email...")
    server.send_message(msg)
    print(f"   ✓ Email sent to {SMTP_USER}")
    
    server.quit()
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Email sent successfully!")
    print("=" * 60)
    print(f"\nCheck your inbox: {SMTP_USER}")
    print("(Also check spam folder)")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED!")
    print(f"Error: {e}")
    print("\nPossible fixes:")
    print("1. Check app password is correct")
    print("2. Enable 2FA on Gmail")
    print("3. Generate new app password")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Type: {type(e).__name__}")

print("\n" + "=" * 60)
