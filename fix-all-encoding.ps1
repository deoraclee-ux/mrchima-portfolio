# Comprehensive Encoding Fix Script
# This fixes ALL encoding issues by replacing corrupted UTF-8 sequences with proper HTML entities

Write-Host "=== Fixing All Encoding Issues ===" -ForegroundColor Cyan

# Define all HTML files to fix
$files = @(
    "index.html",
    "hire.html",
    "source-code.html",
    "projects.html",
    "classes.html",
    "shop.html",
    "inspiration.html",
    "shared/navbar.html",
    "shared/footer.html"
)

# Define replacement patterns
$replacements = @{
    # Corrupted copyright symbols
    'Â©' = '&#169;'
    'Â&#169;' = '&#169;'
    '©' = '&#169;'
    
    # Corrupted em-dash and en-dash
    'â€"' = '&#8212;'
    'â€"' = '&#8211;'
    'ù' = '&#8212;'
    '—' = '&#8212;'
    '–' = '&#8211;'
    
    # Corrupted checkmark
    'âœ"' = '&#x2713;'
    '✓' = '&#x2713;'
    
    # Corrupted naira symbol
    'â‚¦' = '&#8358;'
    '₦' = '&#8358;'
    
    # Corrupted chevron/arrow in CSS content
    'content:"?"' = 'content:"›"'
    'content:"â€"Ç¦"' = 'content:"›"'
    'content:"+â€"+â€"â€"Ç£"' = 'content:"✓"'
    'content:"-â€""' = 'content:"·"'
    'content:"?Â·"' = 'content:"·"'
    
    # Other corrupted symbols
    'â€¢' = '&#8226;'  # bullet
    'â€˜' = '&#8216;'  # left single quote
    'â€™' = '&#8217;'  # right single quote
    'â€œ' = '&#8220;'  # left double quote
    'â€' = '&#8221;'   # right double quote
}

$totalFixed = 0

foreach ($file in $files) {
    $filePath = Join-Path $PSScriptRoot $file
    
    if (-not (Test-Path $filePath)) {
        Write-Host "  [SKIP] $file (not found)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "`n  Processing: $file" -ForegroundColor White
    
    # Read file content as UTF-8
    $content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)
    $originalContent = $content
    $fileChanges = 0
    
    # Apply all replacements
    foreach ($pattern in $replacements.Keys) {
        $replacement = $replacements[$pattern]
        $beforeCount = ([regex]::Matches($content, [regex]::Escape($pattern))).Count
        
        if ($beforeCount -gt 0) {
            $content = $content -replace [regex]::Escape($pattern), $replacement
            $fileChanges += $beforeCount
            Write-Host "    - Fixed $beforeCount occurrence(s) of '$pattern'" -ForegroundColor Green
        }
    }
    
    # Save file if changes were made
    if ($fileChanges -gt 0) {
        # Write as UTF-8 without BOM
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBom)
        
        Write-Host "    [SUCCESS] Fixed $fileChanges issues in $file" -ForegroundColor Green
        $totalFixed += $fileChanges
    } else {
        Write-Host "    [OK] No encoding issues found" -ForegroundColor Gray
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Total issues fixed: $totalFixed" -ForegroundColor $(if ($totalFixed -gt 0) { "Green" } else { "Gray" })
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: git add -A" -ForegroundColor White
Write-Host "2. Run: git commit -m 'Fix all encoding issues across site'" -ForegroundColor White
Write-Host "3. Run: git push" -ForegroundColor White
Write-Host ""
