# Setup Status Checker
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MR CHIMA PORTFOLIO - SETUP STATUS   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()
$success = @()

# 1. Check if modal is injected
Write-Host "[1/7] Checking checkout modal..." -NoNewline
$html = Get-Content "index.html" -Raw -ErrorAction SilentlyContinue
if ($html -and $html -match "checkout-modal") {
    Write-Host " OK" -ForegroundColor Green
    $success += "Checkout modal injected"
} else {
    Write-Host " MISSING" -ForegroundColor Red
    $issues += "Run inject-checkout.ps1"
}

# 2. Check Paystack public key
Write-Host "[2/7] Checking Paystack public key..." -NoNewline
if ($html -and ($html -match "pk_test_" -or $html -match "pk_live_")) {
    Write-Host " OK" -ForegroundColor Green
    $success += "Paystack public key configured"
} else {
    Write-Host " NOT CONFIGURED" -ForegroundColor Yellow
    $warnings += "Update PAYSTACK_PUBLIC_KEY in index.html"
}

# 3. Check backend .env
Write-Host "[3/7] Checking backend .env..." -NoNewline
if (Test-Path "backend\.env") {
    Write-Host " EXISTS" -ForegroundColor Green
    $success += "Backend .env file exists"
} else {
    Write-Host " MISSING" -ForegroundColor Red
    $issues += "Create backend .env from .env.example"
}

# 4. Check Python dependencies
Write-Host "[4/7] Checking Python dependencies..." -NoNewline
try {
    $pipList = py -m pip list 2>&1 | Out-String
    if ($pipList -match "fastapi" -and $pipList -match "uvicorn") {
        Write-Host " OK" -ForegroundColor Green
        $success += "Python dependencies installed"
    } else {
        Write-Host " INCOMPLETE" -ForegroundColor Yellow
        $warnings += "Run: py -m pip install -r backend\requirements.txt"
    }
} catch {
    Write-Host " ERROR" -ForegroundColor Red
    $issues += "Python not found"
}

# 5. Check downloads directory
Write-Host "[5/7] Checking downloads directory..." -NoNewline
if (Test-Path "backend\downloads") {
    Write-Host " EXISTS" -ForegroundColor Green
    
    if (Test-Path "backend\downloads\Oracle-Weather-App.zip") {
        $success += "Oracle-Weather-App.zip found"
    } else {
        $warnings += "Add Oracle-Weather-App.zip to backend\downloads"
    }
    
    if (Test-Path "backend\downloads\mr-chima-ai-agent.zip") {
        $success += "mr-chima-ai-agent.zip found"
    } else {
        $warnings += "Add mr-chima-ai-agent.zip to backend\downloads"
    }
} else {
    Write-Host " MISSING" -ForegroundColor Red
    $issues += "Create backend\downloads directory"
}

# 6. Check profile image
Write-Host "[6/7] Checking profile image..." -NoNewline
if (Test-Path "profile-nobg.png") {
    Write-Host " OK" -ForegroundColor Green
    $success += "Profile image exists"
} else {
    Write-Host " MISSING" -ForegroundColor Yellow
    $warnings += "Add profile-nobg.png"
}

# 7. Check frontend server
Write-Host "[7/7] Checking if frontend is running..." -NoNewline
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host " RUNNING" -ForegroundColor Green
    $success += "Frontend server running on port 8080"
} catch {
    Write-Host " NOT RUNNING" -ForegroundColor Yellow
    $warnings += "Start frontend: npx http-server -p 8080 -c-1"
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "              SUMMARY                   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($success.Count -gt 0) {
    Write-Host "SUCCESS:" -ForegroundColor Green
    foreach ($s in $success) {
        Write-Host "  $s" -ForegroundColor Green
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "WARNINGS:" -ForegroundColor Yellow
    foreach ($w in $warnings) {
        Write-Host "  $w" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($issues.Count -gt 0) {
    Write-Host "ISSUES:" -ForegroundColor Red
    foreach ($i in $issues) {
        Write-Host "  $i" -ForegroundColor Red
    }
    Write-Host ""
}

# Overall status
if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "STATUS: Ready for production!" -ForegroundColor Green
} elseif ($issues.Count -eq 0) {
    Write-Host "STATUS: Ready for testing!" -ForegroundColor Yellow
} else {
    Write-Host "STATUS: Setup incomplete" -ForegroundColor Red
}

Write-Host ""
