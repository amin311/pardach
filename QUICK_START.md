# 🚀 راهنمای سریع - سیستم تست خودکار

## شروع سریع (3 دقیقه)

### 1️⃣ نصب سریع

```bash
# Backend
pip install pytest pytest-django pytest-cov bandit flake8

# Frontend (ممکن است چند دقیقه طول بکشد)
cd frontend
npm install -D cypress@latest eslint eslint-plugin-react cypress-mochawesome-reporter cypress-axe lighthouse-ci
cd ..
```

### 2️⃣ اجرای فوری

```bash
# تست کامل (یک دستور)
python run_all_tests.py

# یا تست‌های جداگانه:

# Backend تست
cd backend && python test_comprehensive.py

# Frontend تست
cd frontend && npm run quality:check

# E2E تست
cd frontend && npm run test:smoke
```

### 3️⃣ مشاهده نتایج

```bash
# گزارش JSON
cat test_report.json

# گزارش HTML (اگر Cypress اجرا شده)
start frontend/cypress/reports/html/index.html
```

## 🎯 تست‌های کلیدی

### تست سریع صفحات (2 دقیقه)

```bash
cd frontend
npm run test:smoke
```

این تست:
- ✅ تمام 16 صفحه اصلی را چک می‌کند
- ✅ خطاهای JavaScript را شناسایی می‌کند  
- ✅ خطاهای API را پیدا می‌کند
- ✅ مشکلات واکنش‌گرایی را تشخیص می‌دهد

### تست امنیتی سریع (1 دقیقه)

```bash
# Backend
cd backend && bandit -r apps/

# Frontend  
cd frontend && npm audit
```

### تست کیفیت کد (30 ثانیه)

```bash
# Backend
cd backend && flake8 apps/

# Frontend
cd frontend && npm run lint
```

## 🔍 خروجی‌های مهم

### ✅ موفقیت
```
🎉 تمام تست‌ها موفق بودند!
📈 نرخ موفقیت: 95.2%
✅ تست‌های موفق: 20
📝 کل تست‌ها: 21
```

### ⚠️ هشدار
```
⚠️ برخی تست‌ها نیاز به بررسی دارند
❌ E2E Tests
❌ Security Analysis
✅ Django Tests
✅ Frontend Lint
```

### ❌ خطا
```
❌ خطا در اجرای تست‌های Django: Connection refused
❌ خطا در اجرای ESLint: 12 errors found
```

## 🛠️ رفع سریع مشکلات

### مشکل: Django نمی‌تواند اتصال برقرار کند
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

### مشکل: Cypress نصب نشده
```bash
cd frontend
npm install cypress --save-dev
npx cypress install
```

### مشکل: ESLint خطا می‌دهد
```bash
cd frontend
npm run lint:fix
```

### مشکل: نصب dependencies ناقص
```bash
# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install

# Backend  
pip install -r requirements.txt
```

## 📊 گزارش سریع

### فایل‌های مهم گزارش:
- `test_report.json` - گزارش کامل JSON
- `frontend/cypress/reports/` - گزارش‌های E2E  
- `frontend/coverage/` - گزارش پوشش کد
- `backend/bandit-report.json` - گزارش امنیتی

### دستورات سریع مشاهده:
```bash
# نمایش گزارش اصلی
cat test_report.json | grep -E "(success_rate|passed_tests|total_tests)"

# نمایش خطاهای امنیتی
cat backend/bandit-report.json | grep -E "(severity|confidence)"

# باز کردن گزارش HTML
start frontend/cypress/reports/html/index.html
```

## 🚀 اتوماسیون

### تست خودکار قبل از Commit
```bash
# اضافه کردن به git hooks
echo "python run_all_tests.py" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### تست روزانه (Windows Task Scheduler)
```bash
# ایجاد batch file
echo "cd /d D:\Gpt engeeneir\sit8" > daily_test.bat
echo "python run_all_tests.py" >> daily_test.bat
echo "pause" >> daily_test.bat
```

### GitHub Actions (خودکار در push)
فایل `.github/workflows/ci.yml` آماده است - فقط commit کنید!

---

## ⏱️ زمان‌بندی تقریبی

| تست | زمان | توضیح |
|-----|------|-------|
| Smoke Tests | 2 دقیقه | تست سریع تمام صفحات |
| Backend Tests | 1 دقیقه | Django + امنیت + کیفیت |
| Frontend Tests | 3 دقیقه | Lint + Unit + Build |
| E2E Complete | 5 دقیقه | تست کامل رابط کاربری |
| **کل** | **10 دقیقه** | تست کامل تمام سیستم |

## 🆘 کمک فوری

### خطا در اجرا؟
1. `python run_all_tests.py --help`
2. مطالعه فایل `AUTOMATED_TESTING_GUIDE.md`
3. بررسی `test_report.json`

### نیاز به تنظیمات؟
1. `frontend/cypress.config.js` - تنظیمات Cypress
2. `frontend/package.json` - اسکریپت‌ها و rules
3. `backend/test_comprehensive.py` - تست‌های Django

### سوال؟
- 📧 Issues در GitHub
- 📖 مطالعه `AUTOMATED_TESTING_GUIDE.md`

**شروع کنید! 🎯** 