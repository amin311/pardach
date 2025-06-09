import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SystemSettings from './SystemSettings';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';

// Mock کردن axios
jest.mock('axios');
// Mock کردن toast
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn()
  }
}));

describe('کامپوننت مدیریت تنظیمات سیستم', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('برای کاربران غیر ادمین پیام دسترسی محدود نمایش دهد', () => {
    render(<SystemSettings isAdmin={false} />);
    expect(screen.getByText('دسترسی محدود')).toBeInTheDocument();
  });

  test('برای ادمین‌ها فرم و لیست تنظیمات را نمایش دهد', async () => {
    // Mock کردن پاسخ دریافت تنظیمات
    axiosInstance.get.mockResolvedValue({
      data: [
        { key: 'max_file_size_mb', value: 5, description: 'حداکثر حجم فایل' }
      ]
    });

    render(<SystemSettings isAdmin={true} />);
    
    // بررسی لودینگ
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    // بررسی نمایش فرم و لیست پس از بارگذاری
    await waitFor(() => {
      expect(screen.getByText('مدیریت تنظیمات سیستم')).toBeInTheDocument();
      expect(screen.getByText('افزودن تنظیم جدید')).toBeInTheDocument();
      expect(screen.getByText('تنظیمات موجود')).toBeInTheDocument();
      expect(screen.getByText('max_file_size_mb')).toBeInTheDocument();
    });
  });

  test('افزودن تنظیم جدید', async () => {
    // Mock کردن پاسخ‌های API
    axiosInstance.get.mockResolvedValue({ data: [] });
    axiosInstance.post.mockResolvedValue({
      data: { key: 'new_setting', value: 10, description: 'توضیح تست' }
    });

    render(<SystemSettings isAdmin={true} />);

    // صبر برای تکمیل لودینگ اولیه
    await waitFor(() => {
      expect(screen.getByText('هیچ تنظیمی یافت نشد')).toBeInTheDocument();
    });

    // پر کردن فرم
    fireEvent.change(screen.getByPlaceholderText('مثال: max_file_size_mb'), {
      target: { value: 'new_setting' }
    });
    fireEvent.change(screen.getByPlaceholderText(/مثال: 5/), {
      target: { value: '10' }
    });
    fireEvent.change(screen.getByPlaceholderText('توضیحات مربوط به این تنظیم'), {
      target: { value: 'توضیح تست' }
    });

    // ارسال فرم
    fireEvent.click(screen.getByText('ذخیره تنظیم'));

    // بررسی فراخوانی API
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith(
        '/api/core/settings/',
        { key: 'new_setting', value: '10', description: 'توضیح تست' },
        expect.any(Object)
      );
      expect(toast.success).toHaveBeenCalledWith('تنظیم با موفقیت اضافه شد');
    });
  });

  test('هنگام بارگذاری با خطا پیام مناسب نمایش دهد', async () => {
    // Mock کردن خطا در API
    axiosInstance.get.mockRejectedValue(new Error('خطای شبکه'));

    render(<SystemSettings isAdmin={true} />);

    await waitFor(() => {
      expect(screen.getByText('خطا در بارگذاری تنظیمات')).toBeInTheDocument();
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری تنظیمات سیستم');
    });
  });
}); 