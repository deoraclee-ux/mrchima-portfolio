"""Test SMTP connection and email sending"""
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@mrchima.dev')
FROM_NAME = 'Abone Chima (Mr Chima)'

print("=" * 60)
print("SMTP Configuration Test")
print("=" * 60)
print(f"Host: {SMTP_HOST}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
print(f"From: {FROM_NAME} <{FROM_EMAIL}>")
print("=" * 60)

try:
    print("\n1. Connecting to SMTP server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    print("   ✓ Connected!")
    
    print("\n2. Starting TLS encryption...")
    server.starttls()
    print("   ✓ TLS started!")
    
    print("\n3. Logging in...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("   ✓ Login successful!")
    
    print("\n4. Sending test email...")
    
    # Create test message
    msg = MIMEMultipart('alternative')
    msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg['To'] = SMTP_USER  # Send to self for testing
    msg['Subject'] = 'Test Email from Mr Chima Portfolio'
    
    text_content = "This is a test email from your portfolio backend. If you received this, SMTP is working!"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #007ACC;">✅ SMTP Test Successful!</h2>
            <p>This is a test email from your <strong>Mr Chima Portfolio</strong> backend.</p>
            <p>If you received this email, your SMTP configuration is working correctly! 🎉</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                From: {FROM_NAME}<br>
                Email: {FROM_EMAIL}<br>
                Server: {SMTP_HOST}:{SMTP_PORT}
            </p>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))
    
    server.send_message(msg)
    print(f"   ✓ Test email sent to {SMTP_USER}!")
    
    print("\n5. Closing connection...")
    server.quit()
    print("   ✓ Connection closed!")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! SMTP is working correctly!")
    print("=" * 60)
    print(f"\nCheck your inbox: {SMTP_USER}")
    print("(Also check spam folder)")
    print("\nIf you received the test email, the problem might be")
    print("with the app password or a temporary Gmail issue.")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED!")
    print(f"   Error: {e}")
    print("\nPossible causes:")
    print("  1. App password is incorrect")
    print("  2. 2-Factor Authentication not enabled")
    print("  3. App password was revoked")
    print("\nFix:")
    print("  1. Go to: https://myaccount.google.com/security")
    print("  2. Enable 2-Step Verification")
    print("  3. Go to: https://myaccount.google.com/apppasswords")
    print("  4. Generate NEW app password")
    print("  5. Update SMTP_PASSWORD in .env (no spaces)")

except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR!")
    print(f"   Error: {e}")
    print("\nPossible causes:")
    print("  1. SMTP server temporarily unavailable")
    print("  2. Port blocked by firewall")
    print("  3. Network connectivity issue")

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR!")
    print(f"   Error: {e}")
    print(f"   Type: {type(e).__name__}")

print("\n" + "=" * 60)
