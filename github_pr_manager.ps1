#!/usr/bin/env pwsh

Write-Host "===== مدیریت Pull Requests GitHub =====" -ForegroundColor Green
Write-Host ""

# تابع برای نمایش menu
function Show-Menu {
    Write-Host "گزینه‌های موجود:" -ForegroundColor Yellow
    Write-Host "1. مشاهده تمام branch های remote"
    Write-Host "2. مشاهده pull request ها (نیاز به GitHub CLI)"
    Write-Host "3. بررسی و merge کردن یک branch"
    Write-Host "4. حذف branch های merge شده"
    Write-Host "5. خروج"
    Write-Host ""
}

do {
    Show-Menu
    $choice = Read-Host "انتخاب شما (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "به‌روزرسانی اطلاعات..." -ForegroundColor Blue
            git fetch origin
            Write-Host "Branch های remote:" -ForegroundColor Blue
            git branch -r
        }
        
        "2" {
            Write-Host "بررسی وجود GitHub CLI..." -ForegroundColor Blue
            if (Get-Command gh -ErrorAction SilentlyContinue) {
                gh pr list
            } else {
                Write-Host "GitHub CLI نصب نیست. لطفاً به آدرس زیر بروید:" -ForegroundColor Red
                Write-Host "https://github.com/YOUR_USERNAME/YOUR_REPO/pulls"
            }
        }
        
        "3" {
            $branchName = Read-Host "نام branch را وارد کنید"
            Write-Host "دریافت آخرین تغییرات..." -ForegroundColor Blue
            git fetch origin
            
            Write-Host "تغییر به branch $branchName..." -ForegroundColor Blue
            git checkout $branchName
            
            Write-Host "تفاوت‌ها با main:" -ForegroundColor Blue
            git diff main..$branchName --stat
            
            Write-Host "Commit های جدید:" -ForegroundColor Blue
            git log main..$branchName --oneline
            
            $confirm = Read-Host "آیا می‌خواهید merge کنید؟ (y/n)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                git checkout main
                git merge $branchName
                git push origin main
                Write-Host "Branch با موفقیت merge شد!" -ForegroundColor Green
            } else {
                git checkout main
                Write-Host "عملیات لغو شد." -ForegroundColor Yellow
            }
        }
        
        "4" {
            Write-Host "حذف branch های merge شده..." -ForegroundColor Blue
            git branch --merged main | Where-Object { $_ -notmatch "main" } | ForEach-Object { git branch -d $_.Trim() }
        }
        
        "5" {
            Write-Host "خروج..." -ForegroundColor Green
            break
        }
        
        default {
            Write-Host "گزینه نامعتبر!" -ForegroundColor Red
        }
    }
    
    if ($choice -ne "5") {
        Write-Host ""
        Read-Host "Enter را برای ادامه فشار دهید"
        Clear-Host
    }
    
} while ($choice -ne "5") 