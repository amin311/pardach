import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../../lib/axios';
import InteractiveGuide from './InteractiveGuide';

// ماک کردن ماژول axios
jest.mock('axios');

// ماک کردن localStorage
const localStorageMock = (function() {
  let store = {};
  return {
    getItem(key) {
      return store[key] || null;
    },
    setItem(key, value) {
      store[key] = value.toString();
    },
    clear() {
      store = {};
    },
    removeItem(key) {
      delete store[key];
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// ماک کردن توابع DOM برای محاسبه موقعیت المان‌ها
global.Element.prototype.getBoundingClientRect = jest.fn(() => ({
  top: 100,
  left: 100,
  width: 200,
  height: 150
}));

window.scrollTo = jest.fn();

describe('آزمون‌های کامپوننت راهنمای تعاملی', () => {
  beforeEach(() => {
    // تنظیم localStorage برای هر تست
    window.localStorage.setItem('access_token', 'fake-token');
    
    // پاکسازی ماک‌ها
    axiosInstance.post.mockClear();
    window.scrollTo.mockClear();
    
    // اضافه کردن المان‌های موردنیاز به DOM
    document.body.innerHTML = `
      <div class="welcome-section"></div>
      <div class="nav-menu-widget"></div>
      <div class="dashboard-widget"></div>
      <div class="orders-widget"></div>
      <div class="notification-widget"></div>
    `;
  });
  
  afterEach(() => {
    // پاکسازی localStorage بین تست‌ها
    window.localStorage.clear();
  });
  
  it('راهنما باید برای کاربری که قبلاً راهنما را ندیده است نمایش داده شود', () => {
    render(<InteractiveGuide userId={1} hasSeenGuide={false} />);
    
    // بررسی نمایش راهنما
    expect(screen.getByText('به سیستم مدیریت سفارش خوش آمدید')).toBeInTheDocument();
    expect(screen.getByText('بعدی')).toBeInTheDocument();
    expect(screen.getByText('پایان راهنما')).toBeInTheDocument();
  });
  
  it('راهنما نباید برای کاربری که قبلاً راهنما را دیده است نمایش داده شود', () => {
    const { container } = render(<InteractiveGuide userId={1} hasSeenGuide={true} />);
    
    // بررسی عدم نمایش راهنما
    expect(container).toBeEmptyDOMElement();
  });
  
  it('کلیک روی دکمه بعدی باید به مرحله بعد برود', () => {
    render(<InteractiveGuide userId={1} hasSeenGuide={false} />);
    
    // مرحله اول
    expect(screen.getByText('به سیستم مدیریت سفارش خوش آمدید')).toBeInTheDocument();
    
    // کلیک روی دکمه بعدی
    fireEvent.click(screen.getByText('بعدی'));
    
    // بررسی نمایش مرحله دوم
    expect(screen.getByText('منوی ناوبری')).toBeInTheDocument();
  });
  
  it('کلیک روی دکمه پایان راهنما باید راهنما را ببندد و وضعیت کاربر را ذخیره کند', async () => {
    axiosInstance.post.mockResolvedValue({ data: { success: true } });
    
    render(<InteractiveGuide userId={1} hasSeenGuide={false} />);
    
    // بررسی نمایش راهنما
    expect(screen.getByText('به سیستم مدیریت سفارش خوش آمدید')).toBeInTheDocument();
    
    // کلیک روی دکمه پایان راهنما
    fireEvent.click(screen.getByText('پایان راهنما'));
    
    // بررسی فراخوانی API
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith(
        '/api/main/settings/',
        {
          key: 'user_1_has_seen_guide',
          value: 'true'
        }
      );
    });
    
    // بررسی عدم نمایش راهنما بعد از کلیک
    expect(screen.queryByText('به سیستم مدیریت سفارش خوش آمدید')).not.toBeInTheDocument();
  });
  
  it('رفتن به مرحله آخر و کلیک روی دکمه پایان باید راهنما را ببندد', async () => {
    axiosInstance.post.mockResolvedValue({ data: { success: true } });
    
    render(<InteractiveGuide userId={1} hasSeenGuide={false} />);
    
    // طی کردن همه مراحل
    for (let i = 0; i < 5; i++) {
      fireEvent.click(screen.getByText('بعدی'));
    }
    
    // بررسی مرحله آخر
    expect(screen.getByText('تبریک!')).toBeInTheDocument();
    
    // کلیک روی دکمه پایان
    fireEvent.click(screen.getByText('پایان'));
    
    // بررسی فراخوانی API
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalled();
    });
    
    // بررسی عدم نمایش راهنما بعد از کلیک
    expect(screen.queryByText('تبریک!')).not.toBeInTheDocument();
  });
  
  it('باید موقعیت المان‌های هدف را محاسبه کند و اسکرول مناسب انجام دهد', () => {
    render(<InteractiveGuide userId={1} hasSeenGuide={false} />);
    
    // بررسی فراخوانی getBoundingClientRect
    expect(global.Element.prototype.getBoundingClientRect).toHaveBeenCalled();
    
    // بررسی فراخوانی scrollTo
    expect(window.scrollTo).toHaveBeenCalled();
  });
}); 