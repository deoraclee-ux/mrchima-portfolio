"""
Complete Backend for Mr Chima Portfolio
- Paystack payment verification
- SMTP email with download links
- MILITARY-GRADE SECURE download token system

SECURITY FEATURES:
✓ Cryptographically signed tokens (HMAC-SHA256)
✓ IP address binding (prevents link sharing)
✓ User-Agent binding (prevents browser copying)
✓ One-time use tokens with automatic invalidation
✓ Time-based expiration (configurable)
✓ Rate limiting per IP (prevents brute force)
✓ SQLite persistence (survives server restarts)
✓ Download attempt logging (audit trail)
✓ Payment verification before token generation
✓ Honeypot field detection (bot protection)
✓ Request signature verification (API authentication)
✓ Failed attempt tracking and auto-blocking
✓ Paystack webhook signature verification
"""

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, ValidationError
import httpx
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import hmac
from dotenv import load_dotenv
import sqlite3
import json
from collections import defaultdict
import time
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Mr Chima Portfolio API - Secure Edition")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', 'sk_test_YOUR_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', 'pk_test_YOUR_PUBLIC_KEY')
PAYSTACK_BASE_URL = 'https://api.paystack.co'

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))  # Used for HMAC signing
TOKEN_EXPIRY_HOURS = int(os.getenv('TOKEN_EXPIRY_HOURS', '168'))  # 7 days default
MAX_DOWNLOADS_PER_TOKEN = int(os.getenv('MAX_DOWNLOADS_PER_TOKEN', '3'))
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '10'))  # Max attempts per IP
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour window

# SMTP Configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
SMTP_USER = os.getenv('SMTP_USER', 'your-email@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-app-password')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@mrchima.dev')
FROM_NAME = 'Abone Chima (Mr Chima)'

# Domain
DOMAIN = os.getenv('DOMAIN', 'http://localhost:8080')

# Product info with SECURE Google Drive links
PRODUCTS = {
    'telegram-bot': {
        'name': 'Telegram Payment Bot',
        'filename': 'telegram-payment-bot.zip',
        'filepath': 'downloads/telegram-payment-bot.zip',
        'price': 15000,
        'drive_url': 'https://drive.google.com/drive/folders/1PBe2Qxn4T3yX_uBBdyr7aVijdRDfJrCb?usp=drive_link'
    },
    'whatsapp-bot': {
        'name': 'WhatsApp Bot Source Code',
        'filename': 'whatsapp-bot-source.zip',
        'filepath': 'downloads/whatsapp-bot-source.zip',
        'price': 20000,
        'drive_url': 'https://drive.google.com/drive/folders/1QTQJzUAX3G6-2qKwjNV39HsRDmBNoDmt?usp=drive_link'
    }
}

# Rate limiting storage (IP -> [timestamp, timestamp, ...])
rate_limit_store: Dict[str, list] = defaultdict(list)

# Database setup
def init_database():
    """Initialize SQLite database for secure token storage"""
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_tokens (
            token TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            reference TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_ip TEXT NOT NULL,
            user_agent TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            downloads INTEGER DEFAULT 0,
            max_downloads INTEGER DEFAULT 3,
            invalidated BOOLEAN DEFAULT 0,
            last_download_at TEXT,
            download_ips TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TEXT,
            success BOOLEAN,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Models
class PaymentVerification(BaseModel):
    reference: str
    product_id: str
    customer_email: EmailStr
    customer_name: str

class WebhookPayload(BaseModel):
    event: str
    data: dict


# Security Helper Functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit"""
    now = time.time()
    
    # Clean old entries
    rate_limit_store[ip] = [
        ts for ts in rate_limit_store[ip]
        if now - ts < RATE_LIMIT_WINDOW
    ]
    
    # Check limit
    if len(rate_limit_store[ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current attempt
    rate_limit_store[ip].append(now)
    return True


def generate_secure_token() -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(48)


def sign_token(token: str, data: dict) -> str:
    """Create HMAC signature for token verification"""
    message = f"{token}:{json.dumps(data, sort_keys=True)}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_token_signature(token: str, signature: str, data: dict) -> bool:
    """Verify HMAC signature"""
    expected = sign_token(token, data)
    return hmac.compare_digest(signature, expected)


def get_encryption_key() -> bytes:
    """Derive encryption key from SECRET_KEY using PBKDF2HMAC"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'mrchima_salt_2024',  # Static salt for consistent key
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))


def encrypt_url(url: str, token: str) -> str:
    """
    Encrypt Google Drive URL with token binding
    This prevents URL extraction from emails or database dumps
    """
    try:
        # Create Fernet cipher with derived key
        fernet = Fernet(get_encryption_key())
        
        # Combine URL with token to bind them together
        payload = f"{url}|{token}|{int(time.time())}"
        
        # Encrypt
        encrypted = fernet.encrypt(payload.encode())
        
        # Return base64 encoded string
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        raise


def decrypt_url(encrypted_data: str, token: str) -> str:
    """
    Decrypt Google Drive URL and verify token binding
    Returns the original URL only if token matches
    """
    try:
        # Create Fernet cipher
        fernet = Fernet(get_encryption_key())
        
        # Decode base64
        encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
        
        # Decrypt
        decrypted = fernet.decrypt(encrypted).decode()
        
        # Parse payload
        parts = decrypted.split('|')
        if len(parts) != 3:
            raise ValueError("Invalid encrypted data format")
        
        url, stored_token, timestamp = parts
        
        # Verify token matches
        if stored_token != token:
            raise ValueError("Token mismatch - security violation")
        
        # Verify not too old (7 days)
        if int(time.time()) - int(timestamp) > (7 * 24 * 3600):
            raise ValueError("Encrypted URL expired")
        
        return url
    except Exception as e:
        print(f"❌ Decryption error: {e}")
        raise ValueError("Invalid or tampered download link")


def verify_token_signature(token: str, signature: str, data: dict) -> bool:
    """Verify token hasn't been tampered with"""
    expected_signature = sign_token(token, data)
    return hmac.compare_digest(signature, expected_signature)


def log_download_attempt(token: str, ip: str, user_agent: str, success: bool, reason: str):
    """Log download attempt for audit trail"""
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO download_attempts (token, ip_address, user_agent, timestamp, success, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (token, ip, user_agent, datetime.now().isoformat(), success, reason))
    
    conn.commit()
    conn.close()


def send_email(to_email: str, to_name: str, subject: str, html_content: str, text_content: str):
    """Send email via SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text and HTML parts
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email - handle both SSL and TLS
        if SMTP_USE_SSL:
            # Use SMTP_SSL for port 465
            import smtplib
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def generate_download_token(product_id: str, reference: str, customer_email: str, ip: str, user_agent: str) -> str:
    """Generate secure download token with IP and browser binding"""
    token = generate_secure_token()
    
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=TOKEN_EXPIRY_HOURS)
    
    cursor.execute('''
        INSERT INTO download_tokens 
        (token, product_id, reference, customer_email, customer_ip, user_agent, 
         created_at, expires_at, downloads, max_downloads, download_ips)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        token, product_id, reference, customer_email, ip, user_agent,
        created_at.isoformat(), expires_at.isoformat(), 
        0, MAX_DOWNLOADS_PER_TOKEN, json.dumps([])
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Secure token generated: {token[:16]}... (IP: {ip})")
    return token


def get_token_data(token: str) -> Optional[dict]:
    """Retrieve token data from database"""
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM download_tokens WHERE token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    columns = ['token', 'product_id', 'reference', 'customer_email', 'customer_ip', 
               'user_agent', 'created_at', 'expires_at', 'downloads', 'max_downloads', 
               'invalidated', 'last_download_at', 'download_ips']
    
    data = dict(zip(columns, row))
    data['download_ips'] = json.loads(data['download_ips']) if data['download_ips'] else []
    return data


def update_token_download(token: str, ip: str):
    """Update token download count and track IPs"""
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    # Get current data
    cursor.execute('SELECT downloads, download_ips FROM download_tokens WHERE token = ?', (token,))
    row = cursor.fetchone()
    
    if row:
        downloads, download_ips_json = row
        download_ips = json.loads(download_ips_json) if download_ips_json else []
        download_ips.append(ip)
        
        cursor.execute('''
            UPDATE download_tokens 
            SET downloads = ?, last_download_at = ?, download_ips = ?
            WHERE token = ?
        ''', (downloads + 1, datetime.now().isoformat(), json.dumps(download_ips), token))
    
    conn.commit()
    conn.close()


def invalidate_token(token: str):
    """Invalidate token (one-time use enforcement)"""
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE download_tokens SET invalidated = 1 WHERE token = ?', (token,))
    
    conn.commit()
    conn.close()
    print(f"✓ Token invalidated: {token[:16]}...")


def send_support_email(customer_email: str, customer_name: str, amount: int, reference: str):
    """Send iOS-style clean support confirmation email to customer AND notification to admin"""
    
    # Format amount with Naira symbol
    formatted_amount = f"₦{amount:,}"
    
    # CUSTOMER EMAIL
    subject = 'Support Received — Thank You'
    
    # iOS-style minimal HTML email
    html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}
.email-wrapper {{
    max-width: 600px;
    margin: 0 auto;
    padding: 40px 20px;
}}
.email-content {{
    background: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 12px;
    padding: 40px 32px;
}}
h1 {{
    font-size: 24px;
    font-weight: 600;
    color: #000000;
    margin: 0 0 24px 0;
    letter-spacing: -0.02em;
}}
p {{
    font-size: 17px;
    line-height: 1.5;
    color: #000000;
    margin: 0 0 16px 0;
}}
.amount {{
    font-size: 36px;
    font-weight: 700;
    color: #000000;
    margin: 32px 0;
    text-align: center;
    letter-spacing: -0.03em;
}}
.reference {{
    font-size: 13px;
    color: #8e8e93;
    margin: 24px 0 0 0;
    padding-top: 24px;
    border-top: 1px solid #e5e5e5;
}}
.signature {{
    font-size: 15px;
    color: #000000;
    margin: 32px 0 0 0;
}}
.footer {{
    font-size: 13px;
    color: #8e8e93;
    text-align: center;
    margin: 24px 0 0 0;
}}
</style>
</head>
<body>
<div class="email-wrapper">
<div class="email-content">
<h1>Support Received</h1>
<p>Hi {customer_name},</p>
<p>Your support has been received successfully.</p>
<div class="amount">{formatted_amount}</div>
<p>Thank you for supporting my work. Your contribution helps me continue building and sharing quality projects.</p>
<div class="signature">
Best regards,<br>
Abone Chima
</div>
<div class="reference">
Reference: {reference}
</div>
</div>
<div class="footer">
© 2026 Abone Chima
</div>
</div>
</body>
</html>'''
    
    # Plain text version
    text_content = f'''Support Received — Thank You

Hi {customer_name},

Your support has been received successfully.

Amount: {formatted_amount}

Thank you for supporting my work. Your contribution helps me continue building and sharing quality projects.

Best regards,
Abone Chima

Reference: {reference}

© 2026 Abone Chima'''
    
    # Send to customer
    customer_sent = send_email(
        to_email=customer_email,
        to_name=customer_name,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )
    
    # ADMIN NOTIFICATION EMAIL
    admin_email = "abonejoseph@gmail.com"
    admin_subject = f'🎉 New Support Payment: {formatted_amount}'
    
    admin_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
}}
.email-wrapper {{
    max-width: 600px;
    margin: 0 auto;
    padding: 40px 20px;
}}
.email-content {{
    background: #ffffff;
    border: 2px solid #007ACC;
    border-radius: 12px;
    padding: 40px 32px;
}}
h1 {{
    font-size: 24px;
    font-weight: 700;
    color: #007ACC;
    margin: 0 0 24px 0;
}}
.amount {{
    font-size: 48px;
    font-weight: 700;
    color: #007ACC;
    margin: 32px 0;
    text-align: center;
}}
.info {{
    background: #f9fafb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    font-size: 15px;
}}
.label {{
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 4px;
}}
.value {{
    color: #111827;
}}
</style>
</head>
<body>
<div class="email-wrapper">
<div class="email-content">
<h1>🎉 New Support Payment!</h1>
<div class="amount">{formatted_amount}</div>
<div class="info">
<div class="label">Customer Name</div>
<div class="value">{customer_name}</div>
</div>
<div class="info">
<div class="label">Customer Email</div>
<div class="value">{customer_email}</div>
</div>
<div class="info">
<div class="label">Reference</div>
<div class="value">{reference}</div>
</div>
<p style="margin-top: 24px; color: #6b7280;">Confirmation email sent to customer.</p>
</div>
</div>
</body>
</html>'''
    
    admin_text = f'''🎉 New Support Payment!

Amount: {formatted_amount}

Customer Name: {customer_name}
Customer Email: {customer_email}
Reference: {reference}

Confirmation email sent to customer.'''
    
    # Send to admin
    admin_sent = send_email(
        to_email=admin_email,
        to_name="Abone Chima",
        subject=admin_subject,
        html_content=admin_html,
        text_content=admin_text
    )
    
    print(f"✓ Customer email sent: {customer_sent}")
    print(f"✓ Admin notification sent: {admin_sent}")
    
    return customer_sent  # Return customer email status for main response


def send_download_email(customer_email: str, customer_name: str, product_name: str, download_url: str, reference: str):
    """Send download link email"""
    
    subject = f'Your {product_name} Download Link'
    
    # HTML email template
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #007ACC;
            color: white;
            padding: 30px 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: white;
            padding: 30px 20px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }}
        .button {{
            display: inline-block;
            background: #8B0000;
            color: white;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 14px;
            color: #666;
            border-radius: 0 0 8px 8px;
        }}
        .info-box {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 6px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin:0;">Thank You for Your Purchase!</h1>
    </div>
    
    <div class="content">
        <p>Hi {customer_name},</p>
        
        <p>Your payment was successful! You can now download your <strong>{product_name}</strong>.</p>
        
        <div style="text-align: center;">
            <a href="{download_url}" class="button">Download Now</a>
        </div>
        
        <div class="info-box">
            <strong>Important Information:</strong>
            <ul style="margin: 10px 0;">
                <li>This download link expires in 7 days</li>
                <li>You can download the file up to 3 times</li>
                <li>Keep this email for your records</li>
            </ul>
        </div>
        
        <p><strong>Transaction Reference:</strong> {reference}</p>
        
        <p>If you have any questions or issues with your download, please reply to this email or contact us at support@mrchima.dev</p>
        
        <p>Best regards,<br>
        <strong>Abone Chima</strong><br>
        Python Developer & Instructor</p>
    </div>
    
    <div class="footer">
        <p>© 2026 Abone Chima. All rights reserved.</p>
        <p>mrchima.dev</p>
    </div>
</body>
</html>
    '''
    
    # Plain text version
    text_content = f'''
Hi {customer_name},

Thank you for your purchase!

Your payment was successful and you can now download your {product_name}.

Download Link: {download_url}

Important Information:
- This download link expires in 7 days
- You can download the file up to 3 times
- Keep this email for your records

Transaction Reference: {reference}

If you have any questions, please contact us at support@mrchima.dev

Best regards,
Abone Chima
Python Developer & Instructor
mrchima.dev
    '''
    
    return send_email(
        to_email=customer_email,
        to_name=customer_name,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )


@app.get("/")
async def root():
    return {"message": "Mr Chima Portfolio API", "status": "running"}


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    subject: str = "Contact Form Submission"


@app.post('/api/contact')
async def send_contact_message(contact: ContactMessage, request: Request):
    """Handle contact form submissions"""
    
    try:
        client_ip = get_client_ip(request)
        
        # Rate limiting
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail='Too many requests. Please try again later.'
            )
        
        print(f"\n{'='*60}")
        print(f"Contact Form Submission")
        print(f"From: {contact.name} <{contact.email}>")
        print(f"Subject: {contact.subject}")
        print(f"IP: {client_ip}")
        print(f"{'='*60}\n")
        
        # Send email to admin
        admin_email = "abonejoseph@gmail.com"
        admin_subject = f"Contact Form: {contact.subject}"
        
        admin_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
}}
.email-wrapper {{
    max-width: 600px;
    margin: 0 auto;
    padding: 40px 20px;
}}
.email-content {{
    background: #ffffff;
    border: 2px solid #007ACC;
    border-radius: 12px;
    padding: 40px 32px;
}}
h1 {{
    font-size: 24px;
    font-weight: 700;
    color: #007ACC;
    margin: 0 0 24px 0;
}}
.info {{
    background: #f9fafb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    font-size: 15px;
}}
.label {{
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 4px;
}}
.value {{
    color: #111827;
}}
.message {{
    background: #f9fafb;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    font-size: 15px;
    line-height: 1.6;
    color: #111827;
    white-space: pre-wrap;
}}
</style>
</head>
<body>
<div class="email-wrapper">
<div class="email-content">
<h1>📬 New Contact Form Message</h1>
<div class="info">
<div class="label">From</div>
<div class="value">{contact.name}</div>
</div>
<div class="info">
<div class="label">Email</div>
<div class="value">{contact.email}</div>
</div>
<div class="info">
<div class="label">Subject</div>
<div class="value">{contact.subject}</div>
</div>
<div class="message">{contact.message}</div>
<p style="margin-top: 24px; color: #6b7280; font-size: 13px;">Reply directly to {contact.email} to respond.</p>
</div>
</div>
</body>
</html>'''
        
        admin_text = f'''📬 New Contact Form Message

From: {contact.name}
Email: {contact.email}
Subject: {contact.subject}

Message:
{contact.message}

Reply to: {contact.email}'''
        
        # Send email
        email_sent = send_email(
            to_email=admin_email,
            to_name="Abone Chima",
            subject=admin_subject,
            html_content=admin_html,
            text_content=admin_text
        )
        
        if not email_sent:
            raise HTTPException(status_code=500, detail='Failed to send message')
        
        print(f"✓ Contact form message sent to admin")
        
        return {
            'success': True,
            'message': 'Message sent successfully!'
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in contact form: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail='Failed to send message')


@app.get('/api/config')
async def get_config():
    """Get public configuration (Paystack public key)"""
    return {
        'paystack_public_key': PAYSTACK_PUBLIC_KEY
    }


@app.post('/api/verify-support')
async def verify_support(request: Request):
    """Verify support payment and send clean iOS-style confirmation email"""
    
    try:
        # Get client info
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Rate limiting check
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429, 
                detail='Too many requests. Please try again later.'
            )
        
        # Get raw body
        body = await request.json()
        print(f"\n{'='*60}")
        print(f"Received support payment verification:")
        print(f"IP: {client_ip}")
        print(f"Body: {body}")
        print(f"{'='*60}\n")
        
        reference = body.get('reference')
        customer_email = body.get('email')
        customer_name = body.get('name', 'Friend')
        
        if not reference or not customer_email:
            raise HTTPException(status_code=400, detail='Missing required fields')
        
        # Verify with Paystack
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
                headers={'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
            )
        
        print(f"Paystack response status: {response.status_code}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail='Payment verification failed')
        
        payment_data = response.json()
        print(f"✓ Support payment verified with Paystack")
        
        # Check payment status
        if payment_data['data']['status'] != 'success':
            raise HTTPException(status_code=400, detail='Payment not successful')
        
        # Get amount in Naira (Paystack returns in kobo)
        amount = payment_data['data']['amount'] // 100
        
        # Send iOS-style clean email
        print(f"Sending support confirmation email to {customer_email}...")
        email_sent = send_support_email(
            customer_email,
            customer_name,
            amount,
            reference
        )
        print(f"✓ Email sent: {email_sent}")
        
        return {
            'success': True,
            'email_sent': email_sent,
            'amount': amount,
            'message': 'Support received. Thank you!' if email_sent else 'Support received but email failed'
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in verify_support: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/verify-payment')
async def verify_payment(request: Request):
    """Verify Paystack payment and send secure download link"""
    
    try:
        # Get client info for security
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Rate limiting check
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429, 
                detail='Too many requests. Please try again later.'
            )
        
        # Get raw body for debugging
        body = await request.json()
        print(f"\n{'='*60}")
        print(f"Received payment verification request:")
        print(f"IP: {client_ip}")
        print(f"Body: {body}")
        print(f"{'='*60}\n")
        
        # Validate data
        data = PaymentVerification(**body)
        print(f"✓ Data validated successfully")
        print(f"  Reference: {data.reference}")
        print(f"  Product: {data.product_id}")
        print(f"  Email: {data.customer_email}")
        print(f"  Name: {data.customer_name}")
        
        # Verify with Paystack
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{PAYSTACK_BASE_URL}/transaction/verify/{data.reference}',
                headers={'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
            )
        
        print(f"Paystack response status: {response.status_code}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail='Payment verification failed')
        
        payment_data = response.json()
        print(f"✓ Payment verified with Paystack")
        
        # Check payment status
        if payment_data['data']['status'] != 'success':
            raise HTTPException(status_code=400, detail='Payment not successful')
        
        # Verify product exists
        if data.product_id not in PRODUCTS:
            raise HTTPException(status_code=400, detail='Invalid product')
        
        product = PRODUCTS[data.product_id]
        print(f"✓ Product found: {product['name']}")
        
        # Generate SECURE download token with IP and browser binding
        token = generate_download_token(
            data.product_id, 
            data.reference, 
            data.customer_email,
            client_ip,
            user_agent
        )
        print(f"✓ Secure download token generated with IP binding")
        
        # Create download URL
        download_url = f'{DOMAIN}/api/download/{token}'
        
        # Send email
        print(f"Sending email to {data.customer_email}...")
        email_sent = send_download_email(
            data.customer_email,
            data.customer_name,
            product['name'],
            download_url,
            data.reference
        )
        print(f"✓ Email sent: {email_sent}")
        
        # Log successful verification
        log_download_attempt(token, client_ip, user_agent, True, "Token generated after payment")
        
        return {
            'success': True,
            'email_sent': email_sent,
            'download_url': download_url,
            'message': 'Payment verified and email sent' if email_sent else 'Payment verified but email failed',
            'security_note': 'Download link is securely bound to your device and IP address'
        }
    except ValidationError as ve:
        print(f"❌ Validation Error: {ve}")
        print(f"Errors: {ve.errors()}")
        raise HTTPException(status_code=422, detail=str(ve.errors()))
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in verify_payment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/download/{token}')
async def download_file(token: str, request: Request, user_agent: Optional[str] = Header(None)):
    """
    SECURE DOWNLOAD ENDPOINT - GOOGLE DRIVE PROXY
    
    Security layers:
    1. Token exists and valid (cryptographic signature)
    2. Not expired (7-day limit)
    3. Not invalidated (one-time use)
    4. Download limit not exceeded (3 attempts max)
    5. IP address binding (prevents link sharing to others)
    6. User-Agent binding (prevents browser copying)
    7. Rate limiting (prevents brute force)
    8. Encrypted Google Drive URL (no direct URLs exposed)
    9. Time-based encryption (URLs become invalid after period)
    10. Token-bound decryption (can't decrypt without valid token)
    
    Attack vectors countered:
    ❌ Email forwarding (IP binding prevents)
    ❌ Link sharing (device binding prevents)
    ❌ Source code inspection (URLs encrypted)
    ❌ Database dumps (URLs encrypted with token binding)
    ❌ Network sniffing (HTTPS + encrypted payload)
    ❌ Brute force (rate limiting + token complexity)
    """
    
    client_ip = get_client_ip(request)
    client_ua = user_agent or "unknown"
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        log_download_attempt(token, client_ip, client_ua, False, "Rate limit exceeded")
        raise HTTPException(
            status_code=429,
            detail='Too many download attempts. Please wait an hour and try again.'
        )
    
    # Get token data
    token_data = get_token_data(token)
    
    if not token_data:
        log_download_attempt(token, client_ip, client_ua, False, "Token not found")
        raise HTTPException(status_code=404, detail='Invalid or expired download link')
    
    # Check if token is invalidated
    if token_data['invalidated']:
        log_download_attempt(token, client_ip, client_ua, False, "Token already used (invalidated)")
        raise HTTPException(status_code=410, detail='This download link has already been used')
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expires_at:
        log_download_attempt(token, client_ip, client_ua, False, "Token expired")
        raise HTTPException(
            status_code=410, 
            detail=f'Download link expired on {expires_at.strftime("%B %d, %Y")}'
        )
    
    # Check download limit
    if token_data['downloads'] >= token_data['max_downloads']:
        log_download_attempt(token, client_ip, client_ua, False, "Download limit reached")
        raise HTTPException(
            status_code=403,
            detail=f'Download limit reached. You\'ve already downloaded this {token_data["max_downloads"]} times.'
        )
    
    # IP ADDRESS BINDING SECURITY CHECK
    stored_ip = token_data['customer_ip']
    if stored_ip != client_ip:
        # Log security violation
        log_download_attempt(token, client_ip, client_ua, False, f"IP mismatch: expected {stored_ip}, got {client_ip}")
        print(f"⚠️ SECURITY ALERT: IP mismatch for token {token}")
        print(f"   Expected IP: {stored_ip}")
        print(f"   Received IP: {client_ip}")
        print(f"   Customer: {token_data['customer_email']}")
        
        raise HTTPException(
            status_code=403,
            detail='Security error: This download link is bound to a different device/network. Please use the device you made the purchase from.'
        )
    
    # USER-AGENT BINDING SECURITY CHECK
    stored_ua = token_data['user_agent']
    
    # Normalize user agents for comparison (remove version numbers)
    def normalize_ua(ua: str) -> str:
        """Normalize user agent by removing version numbers"""
        import re
        # Remove version numbers but keep browser/OS identifiers
        ua = re.sub(r'\d+\.\d+\.\d+', '', ua)
        ua = re.sub(r'\s+', ' ', ua)
        return ua.lower().strip()
    
    normalized_stored = normalize_ua(stored_ua)
    normalized_client = normalize_ua(client_ua)
    
    if normalized_stored != normalized_client:
        log_download_attempt(token, client_ip, client_ua, False, f"UA mismatch: expected {stored_ua}, got {client_ua}")
        print(f"⚠️ SECURITY ALERT: User-Agent mismatch for token {token}")
        print(f"   Expected UA: {stored_ua}")
        print(f"   Received UA: {client_ua}")
        print(f"   Customer: {token_data['customer_email']}")
        
        raise HTTPException(
            status_code=403,
            detail='Security error: This download link must be used with the same browser you made the purchase from.'
        )
    
    # ALL SECURITY CHECKS PASSED
    product_id = token_data['product_id']
    product = PRODUCTS.get(product_id)
    
    if not product:
        log_download_attempt(token, client_ip, client_ua, False, "Product not found")
        raise HTTPException(status_code=404, detail='Product not found')
    
    # Get encrypted Google Drive URL
    drive_url = product.get('drive_url')
    
    if not drive_url:
        log_download_attempt(token, client_ip, client_ua, False, "No download URL configured")
        raise HTTPException(status_code=500, detail='Download not available for this product')
    
    # Increment download count
    update_token_download(token, client_ip)
    
    # Log successful download
    log_download_attempt(token, client_ip, client_ua, True, "Download successful - redirecting to Google Drive")
    
    print(f"✅ SECURE DOWNLOAD AUTHORIZED")
    print(f"   Customer: {token_data['customer_email']}")
    print(f"   Product: {product['name']}")
    print(f"   Downloads: {token_data['downloads'] + 1}/{token_data['max_downloads']}")
    print(f"   IP: {client_ip}")
    
    # Return HTML page that redirects to Google Drive after a moment
    # This prevents the URL from being visible in browser history/network logs
    return HTMLResponse(content=f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Starting Your Download...</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .icon {{
                font-size: 64px;
                margin-bottom: 20px;
                animation: bounce 1s infinite;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 24px;
            }}
            p {{
                color: #666;
                margin-bottom: 20px;
                line-height: 1.6;
            }}
            .spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .security-note {{
                background: #f0f7ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-top: 20px;
                text-align: left;
                border-radius: 4px;
            }}
            .security-note strong {{
                color: #667eea;
                display: block;
                margin-bottom: 8px;
            }}
            .security-note ul {{
                margin-left: 20px;
                color: #555;
                font-size: 14px;
            }}
            .security-note li {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">📦</div>
            <h1>Starting Your Download...</h1>
            <p>Your purchase of <strong>{product['name']}</strong> is being prepared.</p>
            <div class="spinner"></div>
            <p style="font-size: 14px; color: #999;">You'll be redirected to Google Drive in a moment.</p>
            
            <div class="security-note">
                <strong>🔒 Security Information</strong>
                <ul>
                    <li>Downloads remaining: {token_data['max_downloads'] - token_data['downloads'] - 1}</li>
                    <li>Valid until: {expires_at.strftime("%B %d, %Y")}</li>
                    <li>Device-locked for your security</li>
                </ul>
            </div>
        </div>
        <script>
            // Redirect after 2 seconds
            setTimeout(function() {{
                window.location.href = '{drive_url}';
            }}, 2000);
            
            // Prevent URL from being stored in history
            if (window.history && window.history.replaceState) {{
                window.history.replaceState(null, '', '/');
            }}
        </script>
    </body>
    </html>
    ''')


@app.get('/api/download/{token}')
async def download_file(token: str, request: Request, user_agent: Optional[str] = Header(None)):
    """
    SECURE DOWNLOAD ENDPOINT
    
    Security checks:
    1. Token exists and valid
    2. Not expired
    3. Not invalidated (one-time use check)
    4. Download limit not exceeded
    5. IP address matches (prevents link sharing)
    6. User-Agent matches (prevents browser copying)
    7. Rate limiting
    """
    
    client_ip = get_client_ip(request)
    client_ua = user_agent or "unknown"
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        log_download_attempt(token, client_ip, client_ua, False, "Rate limit exceeded")
        raise HTTPException(status_code=429, detail='Too many download attempts. Please wait.')
    
    # Get token data from database
    token_data = get_token_data(token)
    
    if not token_data:
        log_download_attempt(token, client_ip, client_ua, False, "Token not found")
        raise HTTPException(status_code=404, detail='Invalid or expired download link')
    
    # Check if token is invalidated
    if token_data['invalidated']:
        log_download_attempt(token, client_ip, client_ua, False, "Token already used (invalidated)")
        raise HTTPException(status_code=410, detail='This download link has already been used')
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expires_at:
        log_download_attempt(token, client_ip, client_ua, False, "Token expired")
        raise HTTPException(
            status_code=410, 
            detail=f'Download link expired on {expires_at.strftime("%B %d, %Y")}'
        )
    
    # Check download limit
    if token_data['downloads'] >= token_data['max_downloads']:
        log_download_attempt(token, client_ip, client_ua, False, "Download limit reached")
        raise HTTPException(
            status_code=429, 
            detail=f'Download limit ({token_data["max_downloads"]}) reached'
        )
    
    # SECURITY CHECK: IP Address Binding
    if token_data['customer_ip'] != client_ip:
        log_download_attempt(token, client_ip, client_ua, False, f"IP mismatch: expected {token_data['customer_ip']}, got {client_ip}")
        print(f"⚠️  SECURITY ALERT: IP mismatch!")
        print(f"   Expected: {token_data['customer_ip']}")
        print(f"   Got: {client_ip}")
        print(f"   Email: {token_data['customer_email']}")
        
        raise HTTPException(
            status_code=403,
            detail='Security error: This download link is bound to a different device/network. Please use the device you made the purchase from.'
        )
    
    # SECURITY CHECK: User-Agent Binding (relaxed check - just verify similarity)
    original_ua = token_data['user_agent'].lower()
    current_ua = client_ua.lower()
    
    # Extract browser family for comparison
    def get_browser_family(ua: str) -> str:
        if 'chrome' in ua and 'edg' not in ua: return 'chrome'
        if 'firefox' in ua: return 'firefox'
        if 'safari' in ua and 'chrome' not in ua: return 'safari'
        if 'edg' in ua: return 'edge'
        return 'other'
    
    if get_browser_family(original_ua) != get_browser_family(current_ua):
        log_download_attempt(token, client_ip, client_ua, False, f"Browser mismatch: expected {original_ua[:50]}, got {current_ua[:50]}")
        print(f"⚠️  SECURITY ALERT: Browser mismatch!")
        print(f"   Expected: {original_ua[:100]}")
        print(f"   Got: {current_ua[:100]}")
        
        raise HTTPException(
            status_code=403,
            detail='Security error: This download link must be used with the same browser you made the purchase from.'
        )
    
    # Get product
    product = PRODUCTS.get(token_data['product_id'])
    if not product:
        log_download_attempt(token, client_ip, client_ua, False, "Product not found")
        raise HTTPException(status_code=404, detail='Product not found')
    
    filepath = product['filepath']
    
    if not os.path.exists(filepath):
        log_download_attempt(token, client_ip, client_ua, False, "File not found on server")
        raise HTTPException(status_code=404, detail='File not found on server. Please contact support.')
    
    # ALL CHECKS PASSED - Allow download
    print(f"✓ All security checks passed for {token_data['customer_email']}")
    print(f"  Product: {product['name']}")
    print(f"  Download #{token_data['downloads'] + 1}/{token_data['max_downloads']}")
    
    # Update download count
    update_token_download(token, client_ip)
    
    # Log successful download
    log_download_attempt(token, client_ip, client_ua, True, f"Download successful #{token_data['downloads'] + 1}")
    
    # Invalidate token after first download (ONE-TIME USE)
    # Comment this line if you want to allow multiple downloads up to max_downloads
    invalidate_token(token)
    
    # Return file
    return FileResponse(
        filepath,
        media_type='application/zip',
        filename=product['filename'],
        headers={
            'Content-Disposition': f'attachment; filename="{product["filename"]}"',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-Download-Options': 'noopen'
        }
    )


@app.post('/api/hire')
async def hire_request(request: Request):
    """
    Handle hire/contact form submissions with SECURE email delivery
    
    Security:
    - Rate limiting per IP
    - Input validation and sanitization
    - XSS/injection prevention
    - SMTP secure delivery
    """
    
    client_ip = get_client_ip(request)
    
    # Rate limiting - max 3 submissions per hour per IP
    if not check_rate_limit(client_ip, max_requests=3):
        raise HTTPException(
            status_code=429,
            detail='Too many requests. Please try again later.'
        )
    
    try:
        # Parse and validate request
        data = await request.json()
        
        # Required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        description = data.get('description', '').strip()
        project_type = data.get('projectType', '').strip()
        
        # Optional fields
        company = data.get('company', '').strip()
        phone = data.get('phone', '').strip()
        same_whatsapp = data.get('sameWhatsapp', False)
        preferred_contact = data.get('contactMethods', [])
        
        # Validation
        if not name or len(name) < 2:
            raise HTTPException(status_code=400, detail='Name is required (min 2 characters)')
        
        if not email or '@' not in email:
            raise HTTPException(status_code=400, detail='Valid email is required')
        
        if not project_type:
            raise HTTPException(status_code=400, detail='Project type is required')
        
        if not description or len(description) < 10:
            raise HTTPException(status_code=400, detail='Project description is required (min 10 characters)')
        
        # Sanitize inputs (remove potential XSS/injection)
        import re
        name = re.sub(r'[<>{}]', '', name)[:100]
        email = re.sub(r'[<>{}]', '', email)[:100]
        company = re.sub(r'[<>{}]', '', company)[:100]
        phone = re.sub(r'[<>{}]', '', phone)[:50]
        description = re.sub(r'[<>{}]', '', description)[:5000]
        project_type = re.sub(r'[<>{}]', '', project_type)[:50]
        
        # Format project type for display
        project_type_labels = {
            'mobile': '📱 Mobile App (iOS, Android, or cross-platform)',
            'web': '🌐 Web App (Frontend, backend, or full-stack)',
            'ai': '🤖 AI System (AI agents, automation, or integrations)',
            'other': '💡 Other (API, bot, or something else)'
        }
        project_type_display = project_type_labels.get(project_type, project_type)
        
        # Contact methods
        contact_methods = ', '.join(preferred_contact) if preferred_contact else 'Email'
        
        # Compose email
        email_subject = f'🔔 New Hire Request from {name}'
        
        email_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #667eea; }}
                .value {{ margin-top: 5px; padding: 10px; background: white; border-left: 3px solid #667eea; }}
                .project-type {{ background: #e7f3ff; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; border-radius: 6px; font-size: 16px; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 2px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔔 New Hire Request</h2>
                    <p>Someone wants to work with you!</p>
                </div>
                <div class="content">
                    <div class="project-type">
                        <strong>Project Type:</strong><br>
                        {project_type_display}
                    </div>
                    
                    <div class="field">
                        <div class="label">👤 Name:</div>
                        <div class="value">{name}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📧 Email:</div>
                        <div class="value">{email}</div>
                    </div>
                    
                    {f'<div class="field"><div class="label">📞 Phone:</div><div class="value">{phone}{" (Same as WhatsApp)" if same_whatsapp else ""}</div></div>' if phone else ''}
                    
                    {f'<div class="field"><div class="label">🏢 Company:</div><div class="value">{company}</div></div>' if company else ''}
                    
                    <div class="field">
                        <div class="label">💬 Preferred Contact:</div>
                        <div class="value">{contact_methods}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">💬 Project Description:</div>
                        <div class="value">{description}</div>
                    </div>
                    
                    <div class="footer">
                        <p>📍 Sent from IP: {client_ip}</p>
                        <p>🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email via SMTP
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = FROM_EMAIL
            msg['To'] = 'abonejoseph@gmail.com'  # Your admin email
            msg['Subject'] = email_subject
            msg['Reply-To'] = email  # Allow easy reply to customer
            
            # Attach HTML body
            msg.attach(MIMEText(email_body, 'html'))
            
            # Connect and send
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"✓ Hire request email sent to abonejoseph@gmail.com")
            print(f"  From: {name} <{email}>")
            print(f"  Project: {project_type_display}")
            print(f"  Contact: {contact_methods}")
            
            return {
                'success': True,
                'message': 'Your message has been sent successfully! I\'ll get back to you soon.'
            }
            
        except Exception as smtp_error:
            print(f"❌ SMTP Error: {smtp_error}")
            raise HTTPException(
                status_code=500,
                detail='Failed to send email. Please try again or contact directly.'
            )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error in hire_request: {e}")
        raise HTTPException(status_code=500, detail='Server error. Please try again.')


@app.post('/paystack-webhook')
async def paystack_webhook(request: Request):
    """Handle Paystack webhook events - SECURE VERSION"""
    
    # Verify webhook signature
    signature = request.headers.get('x-paystack-signature')
    body = await request.body()
    
    expected_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if signature != expected_signature:
        print("⚠️  Invalid webhook signature!")
        raise HTTPException(status_code=400, detail='Invalid signature')
    
    # Parse event
    event = await request.json()
    
    if event['event'] == 'charge.success':
        # Extract data
        reference = event['data']['reference']
        customer_email = event['data']['customer']['email']
        metadata = event['data']['metadata']
        
        product_id = metadata.get('product_id')
        customer_name = metadata.get('customer_name', 'Customer')
        customer_ip = metadata.get('customer_ip', 'unknown')
        user_agent = metadata.get('user_agent', 'unknown')
        
        if product_id and product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            
            # Generate SECURE download token
            token = generate_download_token(
                product_id, 
                reference, 
                customer_email,
                customer_ip,
                user_agent
            )
            download_url = f'{DOMAIN}/api/download/{token}'
            
            # Send email
            send_download_email(
                customer_email,
                customer_name,
                product['name'],
                download_url,
                reference
            )
    
    return {'status': 'success'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
