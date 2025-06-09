describe('فرآیند احراز هویت', () => {
  beforeEach(() => {
    // پاک کردن localStorage قبل از هر تست
    cy.clearLocalStorage();
  });

  it('باید بتواند ثبت‌نام، ورود و خروج کند', () => {
    // بازدید از صفحه اصلی
    cy.visit('/');
    
    // رفتن به صفحه ثبت‌نام
    cy.contains('ثبت‌نام').click();
    
    // پر کردن فرم ثبت‌نام
    cy.get('[data-cy="username"]').type('testuser');
    cy.get('[data-cy="email"]').type('test@example.com');
    cy.get('[data-cy="password"]').type('testpass123');
    cy.get('[data-cy="first_name"]').type('تست');
    cy.get('[data-cy="last_name"]').type('کاربر');
    
    // ارسال فرم
    cy.get('[data-cy="submit"]').click();
    
    // بررسی موفقیت ثبت‌نام
    cy.url().should('include', '/dashboard');
    cy.contains('خوش آمدید');
    
    // خروج از حساب
    cy.get('[data-cy="logout"]').click();
    
    // بررسی خروج
    cy.url().should('include', '/auth/login');
    
    // ورود مجدد
    cy.get('[data-cy="username"]').type('testuser');
    cy.get('[data-cy="password"]').type('testpass123');
    cy.get('[data-cy="login-submit"]').click();
    
    // بررسی موفقیت ورود
    cy.url().should('include', '/dashboard');
    cy.contains('خوش آمدید');
  });

  it('باید خطای مناسب برای اطلاعات نادرست نشان دهد', () => {
    cy.visit('/auth/login');
    
    // ورود با اطلاعات نادرست
    cy.get('[data-cy="username"]').type('wronguser');
    cy.get('[data-cy="password"]').type('wrongpass');
    cy.get('[data-cy="login-submit"]').click();
    
    // بررسی نمایش خطا
    cy.contains('نام کاربری یا رمز عبور اشتباه است');
  });
});

describe('فرآیند سفارش', () => {
  beforeEach(() => {
    // ورود به عنوان کاربر تست
    cy.login('testuser', 'testpass123');
  });

  it('باید بتواند سفارش جدید ایجاد کند', () => {
    // رفتن به صفحه سفارشات
    cy.visit('/orders');
    
    // کلیک روی ایجاد سفارش جدید
    cy.get('[data-cy="create-order"]').click();
    
    // پر کردن فرم سفارش
    cy.get('[data-cy="order-status"]').select('pending');
    cy.get('[data-cy="order-notes"]').type('سفارش تست');
    
    // انتخاب طرح
    cy.get('[data-cy="design-select"]').click();
    cy.get('[data-cy="design-option"]').first().click();
    
    // تعیین تعداد
    cy.get('[data-cy="quantity"]').clear().type('5');
    
    // ارسال فرم
    cy.get('[data-cy="submit-order"]').click();
    
    // بررسی موفقیت ایجاد سفارش
    cy.contains('سفارش با موفقیت ثبت شد');
    cy.url().should('include', '/orders/');
  });
});

// کامند سفارشی برای ورود
Cypress.Commands.add('login', (username, password) => {
  cy.request({
    method: 'POST',
    url: '/api/auth/login/',
    body: {
      username,
      password
    }
  }).then((response) => {
    window.localStorage.setItem('access_token', response.body.access);
    window.localStorage.setItem('refresh_token', response.body.refresh);
  });
}); 