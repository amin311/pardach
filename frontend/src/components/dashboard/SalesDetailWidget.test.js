import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axiosInstance from '../../lib/axios';
import { toast } from 'react-toastify';
import SalesDetailWidget from './SalesDetailWidget';

// Mock axios
jest.mock('axios');

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  },
}));

// Wrapper component with BrowserRouter
const WrapperComponent = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('SalesDetailWidget', () => {
  // Mock data for testing
  const mockSalesData = {
    total_sales: 12500000,
    total_orders: 75,
    payment_methods: [
      { method: 'online', count: 45, amount: 7500000 },
      { method: 'wallet', count: 20, amount: 3000000 },
      { method: 'credit', count: 10, amount: 2000000 },
    ],
    recent_orders: [
      { id: 1, customer: 'محمد رضایی', amount: 150000, status: 'completed', date: '1402/05/12' },
      { id: 2, customer: 'سارا احمدی', amount: 230000, status: 'processing', date: '1402/05/11' },
    ],
    comparison: {
      sales_increase: 12.5,
      order_increase: 8.3,
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render loading state initially', async () => {
    // Mock axios to return a promise that doesn't resolve immediately
    axiosInstance.get.mockImplementationOnce(() => new Promise(() => {}));

    render(<SalesDetailWidget days={30} />, { wrapper: WrapperComponent });
    
    expect(screen.getByText(/در حال بارگذاری اطلاعات فروش/i)).toBeInTheDocument();
  });

  test('should render sales data when API call succeeds', async () => {
    // Mock successful API response
    axiosInstance.get.mockResolvedValueOnce({ data: mockSalesData });

    render(<SalesDetailWidget days={30} />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByText(/اطلاعات فروش/i)).toBeInTheDocument();
      expect(screen.getByText('12,500,000')).toBeInTheDocument();
      expect(screen.getByText('75')).toBeInTheDocument();
      expect(screen.getByText(/محمد رضایی/i)).toBeInTheDocument();
      expect(screen.getByText(/سارا احمدی/i)).toBeInTheDocument();
      expect(screen.getByText(/12.5%/)).toBeInTheDocument();
    });

    // Check if the API was called with the correct params
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/sales-detail/?days=30');
  });

  test('should show error toast when API call fails', async () => {
    // Mock API error
    const errorMessage = 'خطا در بارگذاری اطلاعات فروش';
    axiosInstance.get.mockRejectedValueOnce(new Error('Network Error'));

    render(<SalesDetailWidget days={30} />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری جزئیات فروش');
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('should render fallback UI when no data available', async () => {
    // Mock response with null data
    axiosInstance.get.mockResolvedValueOnce({ data: null });

    render(<SalesDetailWidget days={30} />, { wrapper: WrapperComponent });

    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByText('اطلاعات فروش موجود نیست')).toBeInTheDocument();
    });
  });

  test('should update data when days prop changes', async () => {
    // First render with 30 days
    axiosInstance.get.mockResolvedValueOnce({ data: mockSalesData });
    const { rerender } = render(<SalesDetailWidget days={30} />, { wrapper: WrapperComponent });
    
    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/sales-detail/?days=30');
    });
    
    // Update to 90 days and mock new response
    axiosInstance.get.mockResolvedValueOnce({ data: { ...mockSalesData, total_orders: 120 } });
    
    rerender(<WrapperComponent><SalesDetailWidget days={90} /></WrapperComponent>);
    
    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/sales-detail/?days=90');
    });
  });
}); 