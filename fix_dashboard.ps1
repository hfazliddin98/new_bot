# Read first 265 lines and save to new file
$lines = Get-Content "dashboard.html" | Select-Object -First 265
$lines | Set-Content "dashboard_fixed.html"
Remove-Item "dashboard.html"
Rename-Item "dashboard_fixed.html" "dashboard.html"
Write-Host "Dashboard file fixed!"
