# 📋 راهنمای مدیریت Pull Request ها

## 🚀 فایل‌های ایجاد شده برای شما:

### 1. `github_status_checker.bat` 
**✨ فایل جدید با قابلیت تشخیص خطا**
- بررسی وجود Git
- نمایش وضعیت repository
- نمایش branch های موجود
- راهنمایی برای مراحل بعدی

### 2. `manage_pull_requests.bat`
**🔍 برای بررسی کلی**
- مشاهده تمام branch ها
- نمایش commit های اخیر

### 3. `review_and_merge_pr.bat`
**⚡ برای merge کردن pull request**
- بررسی تفاوت‌ها
- merge امن با تایید

### 4. `github_pr_manager.ps1`
**🛠️ مدیریت پیشرفته**
- منوی تعاملی
- قابلیت‌های کامل

## 📖 مراحل استفاده:

### مرحله 1: بررسی وضعیت
```
دوبار کلیک روی: github_status_checker.bat
```

### مرحله 2: مشاهده Pull Request ها

#### روش A: مستقیم در GitHub
1. آدرس repository خود را از خروجی مرحله 1 بگیرید
2. به آدرس زیر بروید:
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO/pulls
   ```

#### روش B: GitHub CLI (پیشنهادی)
```cmd
# نصب GitHub CLI
winget install GitHub.cli

# ورود به حساب
gh auth login

# مشاهده pull request ها
gh pr list

# جزئیات یک PR
gh pr view PR_NUMBER
```

### مرحله 3: Merge کردن Pull Request

#### برای merge کردن:
```
دوبار کلیک روی: review_and_merge_pr.bat
نام branch را وارد کنید
```

#### یا دستی:
```cmd
git fetch origin
git checkout BRANCH_NAME
git diff main..BRANCH_NAME  # بررسی تغییرات
git checkout main
git merge BRANCH_NAME
git push origin main
```

## ⚙️ نکات مهم:

### 🔒 امنیت:
- همیشه قبل از merge، تغییرات را بررسی کنید
- از `git diff` برای مشاهده تفاوت‌ها استفاده کنید
- Test های مربوطه را اجرا کنید

### 🧹 نظافت:
- پس از merge، branch های اضافی را حذف کنید:
  ```cmd
  git branch -d BRANCH_NAME  # local
  git push origin --delete BRANCH_NAME  # remote
  ```

### 🚨 عیب‌یابی:
- اگر Git کار نمی‌کند: نصب مجدد کنید
- اگر به GitHub دسترسی ندارید: VPN استفاده کنید
- اگر conflict داشتید: `git mergetool` استفاده کنید

## 📱 دستورات مفید:

```cmd
# مشاهده تمام branch ها
git branch -a

# مشاهده PR های GitHub
gh pr list --state open

# Merge از GitHub CLI
gh pr merge PR_NUMBER --merge

# حذف branch های merge شده
git branch --merged main | findstr /v "main" | xargs git branch -d
```

## 🎯 توصیه‌ها:

1. **استفاده از GitHub CLI**: سریع‌تر و راحت‌تر
2. **بررسی دقیق**: همیشه کد را review کنید
3. **Testing**: قبل از merge تست کنید
4. **Backup**: قبل از تغییرات مهم backup بگیرید

---

💡 **نکته**: اگر مشکلی پیش آمد، تمام فایل‌های `.bat` دارای pause هستند تا بتوانید خطاها را ببینید. 