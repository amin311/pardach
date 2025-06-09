# 🚀 راهنمای سیستم تست خودکار جامع

این سیستم یک پایپ‌لاین کامل کشف خطای خودکار برای پروژه Django-React شما است که تمام صفحات و APIها را به صورت اتوماتیک تست می‌کند.

## 📋 فهرست

- [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
- [اجرای تست‌ها](#اجرای-تستها)
- [انواع تست‌ها](#انواع-تستها)
- [گزارش‌گیری](#گزارشگیری)
- [CI/CD Pipeline](#cicd-pipeline)
- [عیب‌یابی](#عیبیابی)

## 🛠️ نصب و راه‌اندازی

### پیش‌نیازها

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Git
git --version
```

### نصب Dependencies

```bash
# Backend Dependencies
pip install pytest pytest-django pytest-cov bandit flake8

# Frontend Dependencies  
cd frontend
npm install -D cypress@latest eslint eslint-plugin-react cypress-mochawesome-reporter cypress-axe lighthouse-ci
```

## 🚀 اجرای تست‌ها

### اجرای تمام تست‌ها (یک دستور)

```bash
# اجرای کامل تمام تست‌ها
python run_all_tests.py
```

### اجرای تست‌های جداگانه

#### Backend Tests

```bash
# تست‌های Django
cd backend
python manage.py test

# بررسی امنیتی
bandit -r apps/

# بررسی کیفیت کد
flake8 apps/

# تست شامل آنالیز جامع
python test_comprehensive.py
```

#### Frontend Tests

```bash
cd frontend

# ESLint (بررسی کد)
npm run lint

# تست‌های واحد
npm run test:unit

# بررسی امنیتی
npm audit

# ساخت پروژه
npm run build

# تست کیفیت کامل
npm run quality:full
```

#### E2E Tests (Cypress)

```bash
cd frontend

# تست‌های smoke (سریع)
npm run test:smoke

# تمام تست‌های E2E
npm run test:e2e

# باز کردن Cypress UI
npm run cypress:open

# اجرای headless
npm run cypress:run:headless
```

## 🔍 انواع تست‌ها

### 1. 🐍 Backend Tests

| نوع تست | شرح | فایل |
|---------|-----|------|
| Django Unit Tests | تست‌های واحد مدل‌ها و views | `backend/test_comprehensive.py` |
| API Endpoint Tests | تست تمام endpoint های API | `backend/test_apis.py` |
| Security Analysis | آنالیز امنیتی با Bandit | خودکار |
| Code Quality | بررسی کیفیت کد با Flake8 | خودکار |
| System Check | بررسی تنظیمات Django | خودکار |

### 2. ⚛️ Frontend Tests

| نوع تست | شرح | فایل |
|---------|-----|------|
| ESLint | بررسی کیفیت کد JavaScript/React | خودکار |
| Unit Tests | تست‌های واحد کامپوننت‌ها | `src/**/*.test.js` |
| Build Test | تست موفقیت build پروژه | خودکار |
| Security Audit | بررسی آسیب‌پذیری‌های NPM | خودکار |

### 3. 🌐 E2E Tests (Cypress)

| نوع تست | شرح | فایل |
|---------|-----|------|
| Smoke Tests | تست سریع تمام صفحات | `cypress/e2e/smoke_test.cy.js` |
| Auth Flow | تست احراز هویت | `cypress/e2e/auth_flow.cy.js` |
| Navigation | تست ناوبری | `cypress/e2e/navigation.cy.js` |
| Functionality | تست عملکردها | `cypress/e2e/functionality.cy.js` |
| Usability | تست قابلیت استفاده | `cypress/e2e/usability.cy.js` |

### 4. 🔒 Security Tests

- **Backend Security**: Bandit analysis
- **Frontend Security**: NPM audit
- **Dependency Scanning**: Trivy (در CI/CD)
- **OWASP**: Cypress-axe برای دسترسی‌پذیری

### 5. ⚡ Performance Tests

- **Lighthouse CI**: آنالیز عملکرد وب
- **Load Testing**: تست بار صفحات
- **Memory Usage**: بررسی نشت حافظه

## 📊 گزارش‌گیری

### گزارش‌های Local

```bash
# گزارش JSON
cat test_report.json

# گزارش HTML Cypress
open frontend/cypress/reports/html/index.html

# گزارش Coverage
open frontend/coverage/lcov-report/index.html
```

### گزارش‌های CI/CD

- **GitHub Actions**: گزارش در tab Actions
- **Artifacts**: فایل‌های گزارش قابل دانلود
- **PR Comments**: خلاصه نتایج در کامنت‌های PR

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

فایل `.github/workflows/ci.yml` شامل:

1. **Backend Tests**: تست‌های Django + امنیت + کیفیت
2. **Frontend Tests**: ESLint + Unit Tests + Build
3. **E2E Tests**: Cypress headless
4. **Security Scan**: Trivy vulnerability scanner
5. **Performance Test**: Lighthouse CI
6. **Integration Report**: گزارش یکپارچه

### Trigger Events

- **Push** به branch های `main` و `develop`
- **Pull Request** به branch های `main` و `develop`
- **Manual Dispatch** (اجرای دستی)

## 🎯 Smoke Test Coverage

تست خزشگر تمام این صفحات را بررسی می‌کند:

### صفحات عمومی
- `/` - صفحه اصلی
- `/auth/login` - ورود
- `/auth/register` - ثبت‌نام
- `/print-locations` - نقاط چاپ

### صفحات محافظت شده
- `/dashboard` - داشبورد
- `/designs` - طرح‌ها
- `/designs/create` - ایجاد طرح
- `/orders` - سفارش‌ها
- `/profile` - پروفایل
- `/settings` - تنظیمات

### صفحات ادمین
- `/admin/users` - مدیریت کاربران
- `/admin/designs` - مدیریت طرح‌ها

## 🔧 پیکربندی‌ها

### Cypress Configuration

فایل `frontend/cypress.config.js`:
- Base URL: `http://localhost:3000`
- Timeouts: 10 ثانیه
- Screenshots: فعال
- Video: فعال
- Mochawesome reporter: فعال

### ESLint Rules

فایل `frontend/package.json`:
- No console warnings
- No debugger errors
- React hooks rules
- Unused variables warnings

### Coverage Thresholds

- **Functions**: 50%
- **Lines**: 50%
- **Branches**: 50%
- **Statements**: 50%

## 🛠️ عیب‌یابی

### مشکلات رایج

#### 1. خطای Cypress

```bash
# پاک کردن cache
npx cypress cache clear
npx cypress install

# اجرای تست‌ها در حالت debug
npx cypress open
```

#### 2. خطای Django

```bash
# بررسی migrations
python manage.py makemigrations --check

# اجرای migrations
python manage.py migrate

# بررسی تنظیمات
python manage.py check --deploy
```

#### 3. خطای NPM

```bash
# پاک کردن node_modules
rm -rf node_modules package-lock.json
npm install

# بررسی audit
npm audit --audit-level moderate
```

#### 4. خطاهای Memory/Performance

```bash
# افزایش حافظه Node.js
export NODE_OPTIONS="--max-old-space-size=4096"

# اجرای تست‌ها با timeout بیشتر
npm run test:e2e -- --timeout 60000
```

### Debug Commands

```bash
# اجرای تست‌ها با خروجی کامل
python run_all_tests.py --verbose

# تست یک صفحه خاص
npx cypress run --spec "cypress/e2e/smoke_test.cy.js" --browser chrome

# بررسی لاگ‌های دقیق
npm run test:unit -- --verbose
```

## 📝 نکات مهم

1. **همیشه قبل از commit تست‌ها را اجرا کنید**
2. **در صورت fail شدن E2E tests، screenshots را بررسی کنید**
3. **گزارش‌های security را جدی بگیرید**
4. **Coverage کمتر از 50% قابل قبول نیست**
5. **هر performance regression را بررسی کنید**

## 🚀 دستورات سریع

```bash
# همه چیز در یک دستور
python run_all_tests.py

# فقط تست‌های سریع
npm run test:smoke

# فقط تست‌های backend
cd backend && python test_comprehensive.py

# فقط کیفیت frontend
cd frontend && npm run quality:check

# باز کردن گزارش‌ها
npm run report:open
```

---

## 🆘 پشتیبانی

در صورت مواجهه با مشکل:

1. ابتدا [عیب‌یابی](#عیبیابی) را مطالعه کنید
2. لاگ‌های کامل را بررسی کنید
3. فایل `test_report.json` را چک کنید
4. در GitHub Issues گزارش دهید

**موفق باشید! 🎉** 