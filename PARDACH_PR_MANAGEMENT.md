# 🚀 مدیریت Pull Request های پروژه Pardach

## 📊 وضعیت فعلی Repository

**Repository:** [https://github.com/amin311/pardach](https://github.com/amin311/pardach)
- 🔄 **5 Pull Request** در انتظار بررسی
- 👥 **Contributors:** amin311 (شما) و pardach
- 📈 **8 Commit** کل
- 🗂️ **Languages:** JavaScript (58.6%), Python (40.5%), HTML, TypeScript, CSS

## 🎯 مراحل مدیریت Pull Request ها

### مرحله 1: بررسی Pull Request ها

#### روش A: استفاده از فایل اختصاصی
```bash
# دوبار کلیک روی:
pardach_pr_manager.bat
```

#### روش B: مستقیم در GitHub
1. بروید به: [https://github.com/amin311/pardach/pulls](https://github.com/amin311/pardach/pulls)
2. هر PR را جداگانه بررسی کنید
3. کد changes را review کنید
4. نظرات contributor را مطالعه کنید

### مرحله 2: تصمیم‌گیری

برای هر Pull Request باید تصمیم بگیرید:

✅ **Merge:** اگر تغییرات مفید و بدون مشکل است
❌ **Reject:** اگر مشکلی دارد یا مناسب نیست  
💬 **Comment:** اگر نیاز به توضیح یا تغییر دارد

### مرحله 3: اجرای تصمیم

#### برای Merge کردن:

**روش سریع:**
```bash
# در فایل pardach_pr_manager.bat
گزینه 2 را انتخاب کنید
نام branch را وارد کنید
```

**روش دستی:**
```bash
git fetch origin
git checkout main
git merge origin/BRANCH_NAME
git push origin main
```

#### برای Comment کردن:
- مستقیماً در GitHub PR صفحه comment بگذارید
- یا از GitHub CLI استفاده کنید:
```bash
gh pr comment PR_NUMBER --body "متن نظر شما"
```

#### برای Close/Reject کردن:
```bash
gh pr close PR_NUMBER --comment "دلیل reject"
```

## 🔍 بررسی تخصصی

### 1. بررسی Code Quality
```bash
# مشاهده تغییرات
git diff main..origin/BRANCH_NAME

# بررسی commit ها
git log main..origin/BRANCH_NAME --oneline
```

### 2. تست کردن تغییرات
```bash
# تست backend (Django)
cd backend
python manage.py test

# تست frontend (React)  
cd frontend
npm test
```

### 3. بررسی Conflicts
```bash
git merge-base main origin/BRANCH_NAME
git merge --no-commit origin/BRANCH_NAME
```

## ⚡ GitHub CLI Commands (پیشنهادی)

ابتدا GitHub CLI را نصب کنید:
```bash
winget install GitHub.cli
gh auth login
```

سپس از دستورات زیر استفاده کنید:

```bash
# مشاهده تمام PR ها
gh pr list

# جزئیات یک PR
gh pr view PR_NUMBER

# Merge کردن
gh pr merge PR_NUMBER --merge

# Close کردن
gh pr close PR_NUMBER

# Review کردن
gh pr review PR_NUMBER --approve
gh pr review PR_NUMBER --request-changes --body "دلیل تغییر"
```

## 📋 Checklist قبل از Merge

- [ ] کد تمیز و قابل فهم است
- [ ] هیچ conflict وجود ندارد
- [ ] تست‌ها pass می‌شوند
- [ ] دستورالعمل‌های coding standard رعایت شده
- [ ] تغییرات با اهداف پروژه همخوانی دارد
- [ ] Documentation به‌روزرسانی شده (در صورت نیاز)

## 🚨 نکات مهم

### امنیت:
- همیشه کد را review کنید
- از تغییرات مشکوک جلوگیری کنید
- به dependency جدید دقت کنید

### عملکرد:
- تغییرات performance را بررسی کنید
- حجم فایل‌های جدید را چک کنید
- سازگاری با نسخه‌های قبلی را تأیید کنید

### مستندات:
- README به‌روز باشد
- تغییرات مهم مستند شوند
- نحوه استفاده از features جدید توضیح شود

## 🎉 بعد از Merge

1. **پاک‌سازی:**
   - Branch merge شده را از GitHub حذف کنید
   - Local branch های اضافی را پاک کنید

2. **اطلاع‌رسانی:**
   - به contributor تشکر کنید
   - تغییرات مهم را در team اعلام کنید

3. **Testing:**
   - عملکرد کل سیستم را تست کنید
   - اگر مشکلی بود، سریعاً اصلاح کنید

---

💡 **نکته:** همیشه backup از branch اصلی قبل از merge گرفته شود! 