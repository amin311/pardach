@echo off
title GitHub Status Checker
color 0A

echo.
echo ===== بررسی وضعیت GitHub Repository =====
echo.

echo مرحله 1: بررسی وجود Git...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git یافت نشد! لطفاً Git را نصب کنید.
    pause
    exit /b 1
) else (
    echo ✅ Git یافت شد
)

echo.
echo مرحله 2: بررسی repository...
if not exist ".git" (
    echo ❌ این پوشه یک Git repository نیست!
    pause
    exit /b 1
) else (
    echo ✅ Git repository یافت شد
)

echo.
echo مرحله 3: دریافت اطلاعات از GitHub...
git fetch origin 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  خطا در دریافت اطلاعات از GitHub
    echo لطفاً اتصال اینترنت و دسترسی به GitHub را بررسی کنید
) else (
    echo ✅ اطلاعات از GitHub دریافت شد
)

echo.
echo مرحله 4: نمایش branch های موجود...
echo.
echo 📂 Branch های local:
git branch
echo.
echo 📂 Branch های remote:
git branch -r

echo.
echo مرحله 5: نمایش وضعیت repository...
git status --short

echo.
echo ===== اطلاعات کلی =====
echo 🌐 Remote Repository:
git remote -v

echo.
echo 📊 آخرین commit ها:
git log --oneline -5

echo.
echo ===== راهنمای بعدی =====
echo.
echo 1. برای مشاهده pull request ها به GitHub بروید:
echo    🔗 git remote get-url origin (آدرس repository)
echo.
echo 2. برای merge کردن یک branch:
echo    📝 از فایل review_and_merge_pr.bat استفاده کنید
echo.
echo 3. برای نصب GitHub CLI:
echo    💻 winget install GitHub.cli
echo.

pause 