#!/usr/bin/env pwsh

Write-Host "===== ارسال نسخه جدید به GitHub =====" -ForegroundColor Green
Write-Host ""

Write-Host "مرحله 1: اضافه کردن تمام تغییرات..." -ForegroundColor Yellow
git add .

Write-Host "مرحله 2: ایجاد commit جدید..." -ForegroundColor Yellow
git commit -m "New version with model improvements and new features"

Write-Host "مرحله 3: ارسال به GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "===== تمام! نسخه جدید با موفقیت ارسال شد =====" -ForegroundColor Green
Read-Host "Enter را برای خروج فشار دهید" 