@echo off
title Pardach Repository - Pull Request Manager
color 0E

echo.
echo ===== مدیریت Pull Requests پروژه Pardach =====
echo.
echo 🔗 Repository: https://github.com/amin311/pardach
echo 📊 وضعیت: 5 Pull Request در انتظار بررسی
echo.

echo مرحله 1: به‌روزرسانی اطلاعات از GitHub...
git fetch origin

echo.
echo مرحله 2: نمایش branch های remote...
echo 📂 Branch های موجود در GitHub:
git branch -r

echo.
echo مرحله 3: نمایش pull request ها...
echo.
echo 🔄 برای مشاهده جزئیات pull request ها:
echo    👉 https://github.com/amin311/pardach/pulls
echo.

echo مرحله 4: آماده‌سازی برای merge...
echo.

:MENU
echo ===== منوی اقدامات =====
echo 1. مشاهده تفاوت‌های یک branch
echo 2. Merge کردن یک branch
echo 3. باز کردن GitHub در مرورگر
echo 4. نمایش آمار کلی
echo 5. خروج
echo.
set /p choice=انتخاب شما (1-5): 

if "%choice%"=="1" goto SHOW_DIFF
if "%choice%"=="2" goto MERGE_BRANCH  
if "%choice%"=="3" goto OPEN_GITHUB
if "%choice%"=="4" goto SHOW_STATS
if "%choice%"=="5" goto EXIT
goto MENU

:SHOW_DIFF
echo.
set /p branch_name=نام branch را وارد کنید: 
echo.
echo 📊 تفاوت‌های %branch_name% با main:
git fetch origin
git diff main..origin/%branch_name% --stat
echo.
echo 📝 Commit های جدید:
git log main..origin/%branch_name% --oneline --graph
echo.
pause
goto MENU

:MERGE_BRANCH
echo.
set /p branch_name=نام branch برای merge را وارد کنید: 
echo.
echo ⚠️  آیا مطمئن هستید که می‌خواهید %branch_name% را merge کنید؟
set /p confirm=تایید (y/n): 

if /i "%confirm%"=="y" (
    echo.
    echo 🔄 در حال merge کردن %branch_name%...
    git fetch origin
    git checkout main
    git merge origin/%branch_name%
    
    if %errorlevel%==0 (
        echo ✅ Merge موفقیت‌آمیز بود!
        echo 📤 در حال push کردن تغییرات...
        git push origin main
        echo.
        echo 🎉 Pull Request با موفقیت merge شد!
        echo 💡 نکته: branch %branch_name% را از GitHub حذف کنید
    ) else (
        echo ❌ خطا در merge! لطفاً conflict ها را حل کنید
    )
) else (
    echo عملیات لغو شد.
)
echo.
pause
goto MENU

:OPEN_GITHUB
echo.
echo 🌐 باز کردن GitHub در مرورگر...
start https://github.com/amin311/pardach/pulls
echo.
pause
goto MENU

:SHOW_STATS
echo.
echo ===== آمار Repository Pardach =====
echo.
echo 📊 زبان‌های برنامه‌نویسی:
echo    🟨 JavaScript: 58.6%%
echo    🟩 Python: 40.5%%
echo    🟦 HTML: 0.3%%
echo    🟪 TypeScript: 0.3%%
echo    🟫 CSS: 0.1%%
echo.
echo 👥 Contributors:
echo    • amin311 (شما)
echo    • pardach
echo.
echo 📈 آخرین فعالیت‌ها:
git log --oneline -5
echo.
pause
goto MENU

:EXIT
echo.
echo 👋 خروج از مدیریت Pull Requests
echo.
pause
exit 