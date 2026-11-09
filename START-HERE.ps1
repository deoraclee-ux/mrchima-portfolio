# =====================================================
# MR CHIMA PORTFOLIO - COMPLETE SETUP
# =====================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   MR CHIMA PORTFOLIO - QUICK SETUP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Inject checkout modal
Write-Host "[1/5] Injecting checkout modal into HTML..." -ForegroundColor Yellow
try {
    .\inject-checkout.ps1
} catch {
    Write-Host "Note: Checkout modal injection skipped (may already be injected)" -ForegroundColor Gray
}

# Step 2: Check Python
Write-Host ""
Write-Host "[2/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Step 3: Install backend dependencies
Write-Host ""
Write-Host "[3/5] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
try {
    pip install -r requirements.txt -q
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

# Step 4: Check .env file
Write-Host ""
Write-Host "[4/5] Checking configuration..." -ForegroundColor Yellow
if (Test-Path "backend/.env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "! Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "backend/.env.example" "backend/.env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please edit backend/.env with your credentials:" -ForegroundColor Red
    Write-Host "  - Paystack secret key" -ForegroundColor Yellow
    Write-Host "  - Gmail/SMTP settings" -ForegroundColor Yellow
    Write-Host "  - Domain (if not localhost)" -ForegroundColor Yellow
}

# Step 5: Check product files
Write-Host ""
Write-Host "[5/5] Checking product files..." -ForegroundColor Yellow
$downloads = @(
    "backend/downloads/Oracle-Weather-App.zip",
    "backend/downloads/mr-chima-ai-agent.zip"
)

$missingFiles = @()
foreach ($file in $downloads) {
    if (Test-Path $file) {
        Write-Host "✓ $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "✗ $(Split-Path $file -Leaf) - MISSING" -ForegroundColor Red
        $missingFiles += $file
    }
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($missingFiles.Count -gt 0) {
    Write-Host "⚠ Missing product files:" -ForegroundColor Yellow
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Place your ZIP files in backend/downloads/" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure your credentials:" -ForegroundColor White
Write-Host "   notepad backend\.env" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update Paystack public key in index.html:" -ForegroundColor White
Write-Host "   Search for: PAYSTACK_PUBLIC_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the servers:" -ForegroundColor White
Write-Host ""
Write-Host "   Terminal 1 (Frontend):" -ForegroundColor Yellow
Write-Host "   npx http-server -p 8080 -c-1" -ForegroundColor Gray
Write-Host ""
Write-Host "   Terminal 2 (Backend):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Open: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "For detailed guide, see COMPLETE-SETUP-GUIDE.md" -ForegroundColor Cyan
Write-Host ""
