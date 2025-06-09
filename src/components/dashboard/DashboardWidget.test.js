import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../../lib/axios';
import DashboardWidget from './DashboardWidget';
import { toast } from 'react-toastify';

// Mock the dependencies
jest.mock('axios');
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  }
}));

describe('DashboardWidget', () => {
  const mockData = {
    summary: {
      order_count: 5,
      total_sales: 150000,
      unread_notifications: 3,
      report_count: 2
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    axiosInstance.get.mockImplementation(() => new Promise(() => {}));
    
    render(<DashboardWidget />);
    
    expect(screen.getByText('در حال بارگذاری...')).toBeInTheDocument();
  });

  test('renders dashboard data when API call succeeds', async () => {
    axiosInstance.get.mockResolvedValue({ data: mockData });
    
    render(<DashboardWidget />);
    
    await waitFor(() => {
      expect(screen.getByText('خلاصه عملکرد')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument(); // سفارشات
      expect(screen.getByText('150,000')).toBeInTheDocument(); // فروش کل
      expect(screen.getByText('3')).toBeInTheDocument(); // اعلانات
      expect(screen.getByText('2')).toBeInTheDocument(); // گزارش‌ها
    });
    
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/summary/?days=7');
  });

  test('shows error toast when API call fails', async () => {
    const errorMessage = 'خطا در دریافت اطلاعات';
    axiosInstance.get.mockRejectedValue({ message: errorMessage });
    
    render(<DashboardWidget />);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری اطلاعات داشبورد');
    });
  });

  test('renders fallback UI when no data is available', async () => {
    axiosInstance.get.mockResolvedValue({ data: {} });
    
    render(<DashboardWidget />);
    
    await waitFor(() => {
      expect(screen.getByText('اطلاعاتی برای نمایش وجود ندارد')).toBeInTheDocument();
    });
  });
}); 