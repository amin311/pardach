@echo off
echo ===== ارسال نسخه جدید به GitHub =====
echo.

echo مرحله 1: اضافه کردن تمام تغییرات...
git add .

echo مرحله 2: ایجاد commit جدید...
git commit -m "New version with model improvements and new features"

echo مرحله 3: ارسال به GitHub...
git push origin main

echo.
echo ===== تمام! نسخه جدید با موفقیت ارسال شد =====
pause 