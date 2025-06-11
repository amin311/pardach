# سیستم مدیریت سفارش‌ها

این پروژه یک سیستم مدیریت سفارش با رابط کاربری React و بک‌اند Django است. این سیستم به کاربران امکان می‌دهد تا سفارش‌های خود را مدیریت کنند، اعلان‌ها را مشاهده کنند و آمار مربوط به خود را ببینند.

## ویژگی‌های اصلی

- صفحه اصلی با داشبورد کاربر
- نمایش سفارش‌های اخیر
- سیستم اعلان‌ها
- منوی ناوبری کاربرپسند
- اسلایدر تبلیغاتی
- راهنمای تعاملی برای کاربران کم‌تجربه

## پیش‌نیازها

برای اجرای این پروژه به موارد زیر نیاز دارید:

- Python 3.8+
- Node.js 14+
- Django 4.0+
- React 17+
- PostgreSQL یا SQLite

## نصب و راه‌اندازی

### بک‌اند (Django)

1. نصب پیش‌نیازها:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # در لینوکس/مک
   # یا
   venv\Scripts\activate  # در ویندوز
   pip install -r requirements.txt
   ```
   این دستور کتابخانه‌های مورد نیاز مانند
   `djangorestframework-simplejwt`, `drf-spectacular`,
   `django-cors-headers` و `channels` را نیز نصب می‌کند.

2. اجرای مایگریشن‌ها:
   ```bash
   python manage.py migrate
   ```

3. ساخت کاربر ادمین:
   ```bash
   python manage.py createsuperuser
   ```

4. اجرای سرور:
   ```bash
   python manage.py runserver
   ```

### فرانت‌اند (React)

1. نصب وابستگی‌ها:
   ```bash
   cd frontend
   npm install
   # یا
   yarn
   ```

2. اجرای سرور توسعه:
   ```bash
   npm start
   # یا
   yarn start
   ```

3. برای ساخت نسخه تولیدی:
   ```bash
   npm run build
   # یا
   yarn build
   ```

## ساختار پروژه

```
project/
├── backend/                # بک‌اند Django
│   ├── account/            # اپ مربوط به کاربران
│   ├── main/               # اپ صفحه اصلی
│   ├── order/              # اپ مدیریت سفارش‌ها
│   └── notification/       # اپ اعلان‌ها
│
├── frontend/               # فرانت‌اند React
│   ├── public/             # فایل‌های استاتیک عمومی
│   └── src/                # کد منبع React
│       ├── components/     # کامپوننت‌ها
│       │   ├── main/       # کامپوننت‌های صفحه اصلی
│       │   ├── order/      # کامپوننت‌های سفارش
│       │   └── shared/     # کامپوننت‌های مشترک
│       ├── pages/          # صفحات اصلی
│       ├── services/       # سرویس‌های API
│       └── utils/          # توابع کمکی
└── docs/                   # مستندات
```

## مستندات API

مستندات API در آدرس `http://localhost:8000/api/docs/` قابل دسترسی است.

## تست‌ها

### اجرای تست‌های بک‌اند:

```bash
cd backend
python manage.py test
```

### اجرای تست‌های فرانت‌اند:

```bash
cd frontend
npm test
# یا
yarn test
```

## توسعه‌دهندگان

- تیم توسعه سیستم مدیریت سفارش

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. 