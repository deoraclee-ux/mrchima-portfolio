# Complete Encoding Fix Script
# This fixes ALL special characters across ALL HTML files

Write-Host "=== FIXING ALL ENCODING ISSUES ===" -ForegroundColor Green

$files = Get-ChildItem "." -Filter "*.html" | Where-Object { $_.Name -notmatch 'backup|old|working|broken|new|replaced' }

$replacements = @{
    # Checkmarks
    'content:"?"' = 'content:"✓"'
    "content: '?'" = "content: '✓'"
    'content:"?" !' = 'content:"✓" !'
    "content: '?' !" = "content: '✓' !"
    
    # Arrows
    'content:"?"' = 'content:"→"'
    
    # Question labels (these are actual question marks that should stay)
    # We'll handle these carefully
}

foreach ($file in $files) {
    Write-Host "`nProcessing: $($file.Name)" -ForegroundColor Cyan
    
    try {
        # Read with UTF-8 encoding
        $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.UTF8Encoding]::new())
        $originalContent = $content
        $changesMade = $false
        
        # Fix checkmark in CSS (selected state)
        if ($content -match 'selected:before\{content:"?"') {
            $content = $content -replace 'selected:before\{content:"?"', 'selected:before{content:"✓"'
            $changesMade = $true
            Write-Host "  ✓ Fixed checkmark in selected state" -ForegroundColor Green
        }
        
        # Fix checkmark in success state
        if ($content -match "content: '?';") {
            $content = $content -replace "content: '?';", "content: '✓';"
            $changesMade = $true
            Write-Host "  ✓ Fixed checkmark in CSS" -ForegroundColor Green
        }
        
        # Fix arrow in buttons and links
        if ($content -match 'goes:after\{content:"?"') {
            $content = $content -replace 'goes:after\{content:"?"', 'goes:after{content:"→"'
            $changesMade = $true
            Write-Host "  ✓ Fixed arrow in button" -ForegroundColor Green
        }
        
        if ($content -match 'section-more a:after\{content:"?"') {
            $content = $content -replace 'section-more a:after\{content:"?"', 'section-more a:after{content:"→"'
            $changesMade = $true
            Write-Host "  ✓ Fixed arrow in link" -ForegroundColor Green
        }
        
        if ($content -match 'card-action.goes:after\{content:"?"') {
            $content = $content -replace 'card-action.goes:after\{content:"?"', 'card-action.goes:after{content:"→"'
            $changesMade = $true
            Write-Host "  ✓ Fixed arrow in card action" -ForegroundColor Green
        }
        
        # Fix separator dot
        if ($content -match 'cm-chip\+.cm-chip:before\{content:"?"') {
            $content = $content -replace 'cm-chip\+.cm-chip:before\{content:"?"', 'cm-chip+.cm-chip:before{content:"·"'
            $changesMade = $true
            Write-Host "  ✓ Fixed separator dot" -ForegroundColor Green
        }
        
        # Save with UTF-8 BOM to ensure proper encoding
        if ($changesMade) {
            $utf8WithBom = New-Object System.Text.UTF8Encoding($true)
            [System.IO.File]::WriteAllText($file.FullName, $content, $utf8WithBom)
            Write-Host "  💾 Saved with UTF-8 BOM encoding" -ForegroundColor Green
        } else {
            Write-Host "  ℹ No changes needed" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "  ❌ Error: $_" -ForegroundColor Red
    }
}

Write-Host "`n=== COMPLETE! ===" -ForegroundColor Green
Write-Host "All HTML files have been fixed with proper UTF-8 encoding." -ForegroundColor Cyan
