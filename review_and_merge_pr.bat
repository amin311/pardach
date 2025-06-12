@echo off
echo ===== بررسی و Merge کردن Pull Request =====
echo.

set /p BRANCH_NAME=نام branch مورد نظر را وارد کنید: 

echo.
echo مرحله 1: دریافت آخرین تغییرات...
git fetch origin

echo.
echo مرحله 2: تغییر به branch %BRANCH_NAME%...
git checkout %BRANCH_NAME%

echo.
echo مرحله 3: نمایش تفاوت‌ها با main...
git diff main..%BRANCH_NAME%

echo.
echo مرحله 4: نمایش commit های جدید...
git log main..%BRANCH_NAME% --oneline

echo.
echo آیا می‌خواهید این تغییرات را merge کنید؟ (y/n)
set /p CONFIRM=پاسخ شما: 

if /i "%CONFIRM%"=="y" (
    echo.
    echo مرحله 5: تغییر به branch main...
    git checkout main
    
    echo.
    echo مرحله 6: merge کردن %BRANCH_NAME%...
    git merge %BRANCH_NAME%
    
    echo.
    echo مرحله 7: push کردن تغییرات...
    git push origin main
    
    echo.
    echo ===== Pull Request با موفقیت merge شد! =====
) else (
    echo.
    echo عملیات لغو شد.
    git checkout main
)

echo.
pause 