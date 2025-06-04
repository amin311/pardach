# PowerShell script to push changes to GitHub
Write-Host "Changing to project directory..." -ForegroundColor Green
Set-Location "D:\Gpt engeeneir\sit8"

Write-Host "Adding all changes..." -ForegroundColor Yellow
git add -A

Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "feat: major updates including enhanced backend APIs, frontend improvements, and new features - Version 2.0"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
Read-Host "Press Enter to continue..." 