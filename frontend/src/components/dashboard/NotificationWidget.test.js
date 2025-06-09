import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import NotificationWidget from './NotificationWidget';

// Mock axios
jest.mock('axios');

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn()
  },
}));

// Wrapper component with BrowserRouter
const WrapperComponent = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('NotificationWidget', () => {
  // Mock data for testing
  const mockNotifications = [
    {
      id: 1,
      title: 'سفارش جدید',
      message: 'یک سفارش جدید ثبت شده است',
      type: 'order',
      link: '/orders/123',
      read: false,
      created_at_jalali: '1402/05/15'
    },
    {
      id: 2,
      title: 'پرداخت موفق',
      message: 'پرداخت شما با موفقیت انجام شد',
      type: 'payment',
      link: '/payments/456',
      read: false,
      created_at_jalali: '1402/05/14'
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render loading state initially', async () => {
    // Mock axios to return a promise that doesn't resolve immediately
    axiosInstance.get.mockImplementationOnce(() => new Promise(() => {}));

    render(<NotificationWidget />, { wrapper: WrapperComponent });
    
    expect(screen.getByText(/در حال بارگذاری اعلان‌ها/i)).toBeInTheDocument();
  });

  test('should render notifications when API call succeeds', async () => {
    // Mock successful API response
    axiosInstance.get.mockResolvedValueOnce({ data: { results: mockNotifications } });

    render(<NotificationWidget />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByText(/اعلان‌های اخیر/i)).toBeInTheDocument();
      expect(screen.getByText('سفارش جدید')).toBeInTheDocument();
      expect(screen.getByText('پرداخت موفق')).toBeInTheDocument();
      expect(screen.getByText('یک سفارش جدید ثبت شده است')).toBeInTheDocument();
    });

    // Check if the API was called with the correct params
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/notifications/?unread=true&limit=5');
  });

  test('should show error message when API call fails', async () => {
    // Mock API error
    const errorMessage = 'خطا در بارگذاری اعلان‌ها';
    axiosInstance.get.mockRejectedValueOnce(new Error('Network Error'));

    render(<NotificationWidget />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('should display empty state when no notifications', async () => {
    // Mock response with empty array
    axiosInstance.get.mockResolvedValueOnce({ data: { results: [] } });

    render(<NotificationWidget />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByText(/شما هیچ اعلان نخوانده‌ای ندارید/i)).toBeInTheDocument();
    });
  });

  test('should mark notification as read when clicking read button', async () => {
    // Mock successful API responses
    axiosInstance.get.mockResolvedValueOnce({ data: { results: mockNotifications } });
    axiosInstance.patch.mockResolvedValueOnce({ data: { success: true } });

    render(<NotificationWidget />, { wrapper: WrapperComponent });

    // Wait for the component to render notifications
    await waitFor(() => {
      expect(screen.getByText('سفارش جدید')).toBeInTheDocument();
    });

    // Click the "خوانده شد" button on the first notification
    const readButtons = screen.getAllByText('خوانده شد');
    fireEvent.click(readButtons[0]);

    // Wait for the success message to appear
    await waitFor(() => {
      expect(axiosInstance.patch).toHaveBeenCalledWith('/api/notifications/1/', { read: true });
      expect(toast.success).toHaveBeenCalledWith('اعلان خوانده شد');
    });
  });
}); 