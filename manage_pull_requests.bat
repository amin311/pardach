@echo off
echo ===== مدیریت Pull Requests =====
echo.

echo مرحله 1: به‌روزرسانی اطلاعات remote repository...
git fetch origin

echo.
echo مرحله 2: نمایش branch های موجود...
git branch -r

echo.
echo مرحله 3: نمایش آخرین commit های هر branch...
git for-each-ref --format="%(refname:short) %(objectname:short) %(committerdate) %(subject)" refs/remotes/origin

echo.
echo ===== راهنمای استفاده =====
echo برای مشاهده pull request ها:
echo 1. به GitHub بروید: https://github.com/YOUR_USERNAME/YOUR_REPO/pulls
echo 2. یا از GitHub CLI استفاده کنید: gh pr list
echo.
echo برای merge کردن یک pull request:
echo git checkout BRANCH_NAME
echo git merge main
echo git push origin main
echo.
pause 