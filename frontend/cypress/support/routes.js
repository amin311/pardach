// cypress/support/routes.js
export const ROUTES = [
  '/',                           // صفحه اصلی
  '/auth/login',                 // ورود
  '/auth/register',              // ثبت‌نام
  '/dashboard',                  // داشبورد اصلی
  '/designs',                    // لیست طرح‌ها
  '/designs/create',             // ایجاد طرح جدید
  '/designs/batch-upload',       // آپلود دسته‌ای
  '/orders',                     // لیست سفارش‌ها
  '/orders/create',              // ایجاد سفارش جدید
  '/profile',                    // پروفایل کاربر
  '/settings',                   // تنظیمات
  '/admin/users',                // مدیریت کاربران (ادمین)
  '/admin/designs',              // مدیریت طرح‌ها (ادمین)
  '/reports',                    // گزارش‌ها
  '/print-locations',            // نقاط چاپ
  '/business',                   // کسب و کار
];

// مسیرهای محافظت شده که نیاز به احراز هویت دارند
export const PROTECTED_ROUTES = [
  '/dashboard',
  '/designs',
  '/designs/create',
  '/designs/batch-upload',
  '/orders',
  '/orders/create',
  '/profile',
  '/settings',
  '/admin/users',
  '/admin/designs',
  '/reports',
  '/business',
];

// مسیرهای عمومی
export const PUBLIC_ROUTES = [
  '/',
  '/auth/login',
  '/auth/register',
  '/print-locations',
];

// مسیرهای ادمین
export const ADMIN_ROUTES = [
  '/admin/users',
  '/admin/designs',
]; 