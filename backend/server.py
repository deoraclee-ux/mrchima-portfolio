import os
import hmac
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI()

# CORS Configuration
FRONTEND_DOMAIN = os.getenv("DOMAIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_DOMAIN, "https://mrchima-portfolio.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "mrchima_super_secret_key_2024")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "168"))  # 7 days
MAX_DOWNLOADS_PER_TOKEN = int(os.getenv("MAX_DOWNLOADS_PER_TOKEN", "3"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@mrchima.dev")

# Product Configuration
PRODUCTS = {
    "telegram-bot": {
        "name": "Telegram Payment Bot",
        "price": 15000,
        "file": "telegram-payment-bot.zip"
    },
    "whatsapp-bot": {
        "name": "WhatsApp Bot Source Code",
        "price": 20000,
        "file": "whatsapp-bot-source.zip"
    }
}

# Database Setup
def init_db():
    conn = sqlite3.connect("secure_downloads.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS download_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            product_id TEXT NOT NULL,
            email TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            payment_reference TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT NOT NULL,
            downloads_remaining INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            last_used_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            request_count INTEGER NOT NULL,
            window_start TIMESTAMP NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failed_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            reason TEXT NOT NULL,
            attempted_at TIMESTAMP NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Models
class PaymentVerification(BaseModel):
    reference: str
    product_id: str
    email: EmailStr
    name: str
    fingerprint: str

class DownloadRequest(BaseModel):
    token: str
    fingerprint: str

# Security Functions
def generate_secure_token(product_id: str, email: str, reference: str) -> str:
    """Generate HMAC-SHA256 signed token"""
    random_part = secrets.token_urlsafe(32)
    message = f"{product_id}:{email}:{reference}:{random_part}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{random_part}.{signature}"

def verify_token_signature(token: str, product_id: str, email: str, reference: str) -> bool:
    """Verify HMAC-SHA256 token signature"""
    try:
        random_part, signature = token.split(".")
        message = f"{product_id}:{email}:{reference}:{random_part}"
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except:
        return False

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP has exceeded rate limit"""
    conn = sqlite3.connect("secure_downloads.db")
    cursor = conn.cursor()
    
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    cursor.execute(
        "SELECT request_count FROM rate_limits WHERE ip_address = ? AND window_start > ?",
        (ip_address, window_start)
    )
    result = cursor.fetchone()
    
    if result and result[0] >= RATE_LIMIT_REQUESTS:
        conn.close()
        return False
    
    if result:
        cursor.execute(
            "UPDATE rate_limits SET request_count = request_count + 1 WHERE ip_address = ?",
            (ip_address,)
        )
    else:
        cursor.execute(
            "INSERT INTO rate_limits (ip_address, request_count, window_start) VALUES (?, 1, ?)",
            (ip_address, now)
        )
    
    conn.commit()
    conn.close()
    return True

def log_failed_attempt(ip_address: str, reason: str):
    """Log failed download attempt"""
    conn = sqlite3.connect("secure_downloads.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO failed_attempts (ip_address, reason, attempted_at) VALUES (?, ?, ?)",
        (ip_address, reason, datetime.now())
    )
    conn.commit()
    conn.close()

async def verify_paystack_payment(reference: str) -> dict:
    """Verify payment with Paystack"""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

async def send_download_email(email: str, name: str, product: str, download_url: str, reference: str):
    """Send download link via email"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Your {product} Download Link"
        message["From"] = FROM_EMAIL
        message["To"] = email
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4CAF50;">Thank You for Your Purchase!</h2>
              <p>Hi {name},</p>
              <p>Thank you for purchasing <strong>{product}</strong>.</p>
              <p>Your payment reference: <code>{reference}</code></p>
              <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Download Link:</strong></p>
                <a href="{download_url}" style="display: inline-block; margin-top: 10px; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Download Now</a>
              </div>
              <p><strong>Important Notes:</strong></p>
              <ul>
                <li>This link is valid for {TOKEN_EXPIRY_HOURS // 24} days</li>
                <li>You can download up to {MAX_DOWNLOADS_PER_TOKEN} times</li>
                <li>This link is secured and tied to your device</li>
              </ul>
              <p>If you have any questions, feel free to reach out!</p>
              <p>Best regards,<br>Mr. Chima</p>
            </div>
          </body>
        </html>
        """
        
        message.attach(MIMEText(html, "html"))
        
        if SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Mr. Chima Portfolio API", "status": "running"}

@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "paystack_public_key": PAYSTACK_PUBLIC_KEY,
        "products": PRODUCTS
    }

@app.post("/api/verify-payment")
async def verify_payment(payment: PaymentVerification, request: Request):
    """Verify payment and generate secure download token"""
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Rate limiting
    if not check_rate_limit(ip_address):
        log_failed_attempt(ip_address, "Rate limit exceeded")
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Validate product
    if payment.product_id not in PRODUCTS:
        log_failed_attempt(ip_address, f"Invalid product: {payment.product_id}")
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    # Verify with Paystack
    paystack_response = await verify_paystack_payment(payment.reference)
    
    if not paystack_response.get("status"):
        log_failed_attempt(ip_address, "Paystack verification failed")
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    data = paystack_response.get("data", {})
    
    if data.get("status") != "success":
        log_failed_attempt(ip_address, f"Payment status: {data.get('status')}")
        raise HTTPException(status_code=400, detail="Payment was not successful")
    
    # Verify amount
    expected_amount = PRODUCTS[payment.product_id]["price"] * 100  # Paystack uses kobo
    if data.get("amount") != expected_amount:
        log_failed_attempt(ip_address, "Amount mismatch")
        raise HTTPException(status_code=400, detail="Payment amount mismatch")
    
    # Generate secure token
    token = generate_secure_token(payment.product_id, payment.email, payment.reference)
    
    # Store token in database
    conn = sqlite3.connect("secure_downloads.db")
    cursor = conn.cursor()
    
    now = datetime.now()
    expires_at = now + timedelta(hours=TOKEN_EXPIRY_HOURS)
    
    try:
        cursor.execute("""
            INSERT INTO download_tokens 
            (token, product_id, email, customer_name, payment_reference, ip_address, user_agent, 
             downloads_remaining, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            token, payment.product_id, payment.email, payment.name, payment.reference,
            ip_address, user_agent, MAX_DOWNLOADS_PER_TOKEN, now, expires_at
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # Token already exists (duplicate payment reference)
        cursor.execute(
            "SELECT token FROM download_tokens WHERE payment_reference = ?",
            (payment.reference,)
        )
        result = cursor.fetchone()
        if result:
            token = result[0]
    finally:
        conn.close()
    
    # Generate download URL
    download_url = f"{FRONTEND_DOMAIN}/download?token={token}&product={payment.product_id}"
    
    # Send email
    product_name = PRODUCTS[payment.product_id]["name"]
    email_sent = await send_download_email(
        payment.email, payment.name, product_name, download_url, payment.reference
    )
    
    return {
        "success": True,
        "download_url": download_url,
        "token": token,
        "email_sent": email_sent,
        "expires_at": expires_at.isoformat()
    }

@app.post("/api/download")
async def download_file(download: DownloadRequest, request: Request):
    """Download file with secure token"""
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Rate limiting
    if not check_rate_limit(ip_address):
        log_failed_attempt(ip_address, "Rate limit exceeded on download")
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Get token from database
    conn = sqlite3.connect("secure_downloads.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT product_id, email, payment_reference, ip_address, user_agent, 
               downloads_remaining, expires_at
        FROM download_tokens
        WHERE token = ?
    """, (download.token,))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        log_failed_attempt(ip_address, "Invalid token")
        raise HTTPException(status_code=404, detail="Invalid download token")
    
    (product_id, email, reference, stored_ip, stored_ua, 
     downloads_remaining, expires_at) = result
    
    # Check expiration
    if datetime.now() > datetime.fromisoformat(expires_at):
        conn.close()
        log_failed_attempt(ip_address, "Token expired")
        raise HTTPException(status_code=403, detail="Download link has expired")
    
    # Check downloads remaining
    if downloads_remaining <= 0:
        conn.close()
        log_failed_attempt(ip_address, "No downloads remaining")
        raise HTTPException(status_code=403, detail="Download limit reached")
    
    # Verify IP and User-Agent (browser fingerprint)
    if stored_ip != ip_address:
        conn.close()
        log_failed_attempt(ip_address, "IP mismatch")
        raise HTTPException(status_code=403, detail="Security check failed: IP address mismatch")
    
    if stored_ua != user_agent:
        conn.close()
        log_failed_attempt(ip_address, "User-Agent mismatch")
        raise HTTPException(status_code=403, detail="Security check failed: Browser fingerprint mismatch")
    
    # Verify token signature
    if not verify_token_signature(download.token, product_id, email, reference):
        conn.close()
        log_failed_attempt(ip_address, "Invalid signature")
        raise HTTPException(status_code=403, detail="Invalid token signature")
    
    # Update downloads remaining
    cursor.execute("""
        UPDATE download_tokens
        SET downloads_remaining = downloads_remaining - 1,
            last_used_at = ?
        WHERE token = ?
    """, (datetime.now(), download.token))
    
    conn.commit()
    conn.close()
    
    # Serve file
    product = PRODUCTS.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    file_path = os.path.join("downloads", product["file"])
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/zip",
        filename=product["file"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
