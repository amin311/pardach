import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../../lib/axios';
import DashboardPage from './DashboardPage';
import { toast } from 'react-toastify';

// Mock the dependencies
jest.mock('axios');
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
    info: jest.fn(),
  }
}));

// Mock Chart.js to avoid canvas rendering issues
jest.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="line-chart">Chart Mocked</div>,
  Bar: () => <div data-testid="bar-chart">Chart Mocked</div>,
}));

// Mock components
jest.mock('../../components/dashboard/SalesDetailWidget', () => () => <div data-testid="sales-widget"></div>);
jest.mock('../../components/dashboard/BusinessDetailWidget', () => () => <div data-testid="business-widget"></div>);
jest.mock('../../components/dashboard/NotificationWidget', () => () => <div data-testid="notification-widget"></div>);
jest.mock('../../components/dashboard/ReportWidget', () => () => <div data-testid="report-widget"></div>);
jest.mock('../../components/dashboard/DashboardStatsWidget', () => ({ stats }) => <div data-testid="stats-widget">{stats.length} stats</div>);
jest.mock('../../components/dashboard/DashboardChartWidget', () => ({ title }) => <div data-testid="chart-widget">{title}</div>);
jest.mock('../../components/dashboard/DashboardGuide', () => ({ userId, hasSeenGuide }) => (
  <div data-testid="dashboard-guide" data-user-id={userId} data-has-seen-guide={hasSeenGuide.toString()}></div>
));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('DashboardPage', () => {
  const mockSummaryData = {
    summary: {
      order_count: 75,
      total_sales: 12500000,
      payment_count: 68,
      unread_notifications: 4,
      report_count: 12,
      total_payments: 11800000
    },
    charts: {
      orders: {
        title: 'آمار سفارش‌ها',
        labels: ['فروردین', 'اردیبهشت', 'خرداد'],
        values: [12, 19, 8]
      },
      payments: {
        title: 'آمار پرداخت‌ها',
        labels: ['فروردین', 'اردیبهشت', 'خرداد'],
        values: [10, 15, 7]
      }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    axiosInstance.get.mockResolvedValue({ data: mockSummaryData });
  });

  test('renders loading state initially', () => {
    axiosInstance.get.mockImplementation(() => new Promise(() => {}));
    
    render(<DashboardPage />);
    
    expect(screen.getByText('در حال بارگذاری...')).toBeInTheDocument();
  });

  test('renders dashboard data when API call succeeds', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('داشبورد مدیریت')).toBeInTheDocument();
      expect(screen.getByText('75')).toBeInTheDocument(); // تعداد سفارشات
      expect(screen.getByText('12,500,000')).toBeInTheDocument(); // فروش کل
      expect(screen.getByText('68')).toBeInTheDocument(); // تعداد پرداخت‌ها
      expect(screen.getByText('4')).toBeInTheDocument(); // اعلانات خوانده نشده
      expect(screen.getByText('12')).toBeInTheDocument(); // تعداد گزارش‌ها
    });
    
    // Check for charts
    expect(screen.getAllByTestId('line-chart').length).toBeGreaterThan(0);
    expect(screen.getAllByTestId('bar-chart').length).toBeGreaterThan(0);
    
    // Default days filter is 30
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/summary/?days=30');
  });

  test('changes data range when time filter changes', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('داشبورد مدیریت')).toBeInTheDocument();
    });
    
    // Change time filter to 7 days
    const select = screen.getByLabelText('بازه زمانی:');
    fireEvent.change(select, { target: { value: '7' } });
    
    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/summary/?days=7');
    });
  });

  test('shows error toast when API call fails', async () => {
    const errorMessage = 'خطا در دریافت اطلاعات';
    axiosInstance.get.mockRejectedValue({ message: errorMessage });
    
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری اطلاعات داشبورد');
    });
  });

  test('renders properly without chart data', async () => {
    const noChartData = {
      summary: { ...mockSummaryData.summary },
      charts: {}
    };
    
    axiosInstance.get.mockResolvedValue({ data: noChartData });
    
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('داشبورد مدیریت')).toBeInTheDocument();
      expect(screen.getByText('اطلاعات نموداری موجود نیست')).toBeInTheDocument();
    });
  });
}); 