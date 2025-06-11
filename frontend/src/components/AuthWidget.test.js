import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AuthWidget from './AuthWidget';
import axiosInstance from '../lib/axios';
import { toast } from 'react-toastify';

// Mock مورد نیاز
jest.mock('axios');
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn()
  }
}));
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>
  }
}));

describe('کامپوننت AuthWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('ابتدا فرم ورود نمایش داده می‌شود', () => {
    render(<AuthWidget setUser={jest.fn()} />);
    expect(screen.getByText('ورود به حساب کاربری')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('نام کاربری')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('رمز عبور')).toBeInTheDocument();
    expect(screen.getByText('ورود')).toBeInTheDocument();
  });

  test('تغییر به فرم ثبت‌نام', () => {
    render(<AuthWidget setUser={jest.fn()} />);
    
    // کلیک روی لینک ثبت‌نام
    fireEvent.click(screen.getByText('ثبت‌نام کنید'));
    
    // بررسی نمایش فرم ثبت‌نام
    expect(screen.getByText('ثبت‌نام در سیستم')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('ایمیل')).toBeInTheDocument();
    expect(screen.getByText('ثبت‌نام')).toBeInTheDocument();
  });

  test('ارسال فرم ورود', async () => {
    const mockSetUser = jest.fn();
    const mockResponse = {
      data: {
        access: 'test_access_token',
        refresh: 'test_refresh_token',
        user: { username: 'testuser' }
      }
    };
    
    axiosInstance.post.mockResolvedValue(mockResponse);
    
    render(<AuthWidget setUser={mockSetUser} />);
    
    // پر کردن فرم
    fireEvent.change(screen.getByLabelText('نام کاربری'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('رمز عبور'), { target: { value: 'password123' } });
    
    // ارسال فرم
    fireEvent.submit(screen.getByRole('button', { name: /ورود/i }));
    
    // منتظر اتمام درخواست
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/login/', {
        username: 'testuser',
        password: 'password123'
      });
      expect(toast.success).toHaveBeenCalledWith('ورود موفق');
      expect(mockSetUser).toHaveBeenCalledWith({ username: 'testuser' });
      expect(localStorage.getItem('access_token')).toBe('test_access_token');
    });
  });

  test('ارسال فرم ثبت‌نام', async () => {
    const mockSetUser = jest.fn();
    const mockResponse = {
      data: {
        access: 'test_access_token',
        refresh: 'test_refresh_token',
        user: { username: 'newuser' }
      }
    };
    
    axiosInstance.post.mockResolvedValue(mockResponse);
    
    render(<AuthWidget setUser={mockSetUser} />);
    
    // تغییر به فرم ثبت‌نام
    fireEvent.click(screen.getByText('ثبت‌نام کنید'));
    
    // پر کردن فرم
    fireEvent.change(screen.getByLabelText('نام کاربری'), { target: { value: 'newuser' } });
    fireEvent.change(screen.getByLabelText('ایمیل'), { target: { value: 'new@example.com' } });
    fireEvent.change(screen.getByLabelText('رمز عبور'), { target: { value: 'password123' } });
    
    // ارسال فرم
    fireEvent.submit(screen.getByRole('button', { name: /ثبت‌نام/i }));
    
    // منتظر اتمام درخواست
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/auth/register/', {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
        first_name: '',
        last_name: ''
      });
      expect(toast.success).toHaveBeenCalledWith('ثبت‌نام موفق');
      expect(mockSetUser).toHaveBeenCalledWith({ username: 'newuser' });
    });
  });

  test('نمایش خطا در صورت مشکل در ورود', async () => {
    axiosInstance.post.mockRejectedValue(new Error('Login failed'));
    
    render(<AuthWidget setUser={jest.fn()} />);
    
    // پر کردن و ارسال فرم
    fireEvent.change(screen.getByLabelText('نام کاربری'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('رمز عبور'), { target: { value: 'wrongpassword' } });
    fireEvent.submit(screen.getByRole('button', { name: /ورود/i }));
    
    // منتظر اتمام درخواست
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در ورود');
    });
  });
}); 