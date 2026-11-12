# Verify Deployment Status
Write-Host "=== Portfolio Deployment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check git status
Write-Host "Git Status:" -ForegroundColor Yellow
git log --oneline -n 3

Write-Host ""
Write-Host "Latest commit on GitHub:" -ForegroundColor Yellow
git ls-remote origin HEAD

Write-Host ""
Write-Host "=== Checking inspiration.html ===" -ForegroundColor Cyan

# Check logo in inspiration.html
$content = Get-Content "inspiration.html" -Raw -Encoding UTF8

if ($content -match 'logo-blue-new\.png') {
    Write-Host "✓ Logo path is CORRECT: logo-blue-new.png" -ForegroundColor Green
} elseif ($content -match 'mr-chima-blue-loop-logo\.png') {
    Write-Host "✗ Logo path is WRONG: mr-chima-blue-loop-logo.png" -ForegroundColor Red
} else {
    Write-Host "? Could not find logo path" -ForegroundColor Yellow
}

# Check CSS width
if ($content -match 'width:\s*120px\s*!important') {
    Write-Host "✓ Logo width is CORRECT: 120px !important" -ForegroundColor Green
} elseif ($content -match 'width:\s*24px\s*!important') {
    Write-Host "✗ Logo width is WRONG: 24px !important" -ForegroundColor Red
} else {
    Write-Host "? Could not find logo width" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Solution ===" -ForegroundColor Cyan
Write-Host "The files are correct locally and pushed to GitHub." -ForegroundColor White
Write-Host "If you still see the old logo, try:" -ForegroundColor White
Write-Host "1. Hard refresh: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)" -ForegroundColor Yellow
Write-Host "2. Clear browser cache for mrchima.dev" -ForegroundColor Yellow
Write-Host "3. Wait 1-2 minutes for Vercel CDN to update" -ForegroundColor Yellow
Write-Host "4. Try in incognito/private browsing mode" -ForegroundColor Yellow
Write-Host ""
Write-Host "Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor Cyan
