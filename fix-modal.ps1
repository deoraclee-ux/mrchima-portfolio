# Fix Modal onclick handlers
$file = 'index.html'
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Original file size: $($content.Length) bytes"

# Pattern 1: Oracle Weather App
$pattern1 = '(<span class="card-action goes">Get the code</span>)(</div></div></a><a class="card"[^>]*?>.*?mr-joseph)'
if ($content -match $pattern1) {
    Write-Host "Found Oracle Weather pattern"
    # Check context around it
    $idx = $content.IndexOf('Oracle Weather App')
    if ($idx -gt 0) {
        $before = $content.Substring([Math]::Max(0, $idx-100), 100)
        $after = $content.Substring($idx, [Math]::Min(200, $content.Length - $idx))
        Write-Host "Context: ...$before [ORACLE] $after..."
    }
}

# Try simpler replacement
$old1 = '<span class="card-action goes">Get the code</span></div></div></a><a class="card" href="javascript:void(0)" role="button" style="cursor:pointer"><div class="card-body"><div class="zip-head"><span class="zip-icon" aria-hidden="true"><i class="zip-teeth"></i><b>ZIP</b></span><span class="zip-file"><span class="zip-name">mr-joseph.zip'

$new1 = '<span class="card-action goes" onclick="openCheckout(''oracle-weather'', ''Oracle Weather App'', 15000)">Get the code</span></div></div></a><a class="card" href="javascript:void(0)" role="button" style="cursor:pointer"><div class="card-body"><div class="zip-head"><span class="zip-icon" aria-hidden="true"><i class="zip-teeth"></i><b>ZIP</b></span><span class="zip-file"><span class="zip-name">mr-joseph.zip'

if ($content.Contains($old1)) {
    Write-Host "✓ Found exact Oracle pattern, replacing..."
    $content = $content.Replace($old1, $new1)
} else {
    Write-Host "✗ Exact pattern not found"
}

# Save
Set-Content -Path $file -Value $content -Encoding UTF8 -NoNewline
Write-Host "File updated: $($content.Length) bytes"

# Verify
if ($content.Contains("onclick=")) {
    Write-Host "✓✓✓ onclick handler added successfully!"
} else {
    Write-Host "✗✗✗ onclick handler NOT added"
}
