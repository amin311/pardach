import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../../api/axiosInstance';
import { BrowserRouter } from 'react-router-dom';
import BusinessDetailWidget from './BusinessDetailWidget';
import { toast } from 'react-toastify';

// Mock the dependencies
jest.mock('axios');
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  }
}));

const WrapperComponent = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('BusinessDetailWidget', () => {
  const mockData = {
    total_businesses: 10,
    active_businesses: 8,
    recent_activities: [
      {
        id: '1',
        business_id: '101',
        business_name: 'کسب‌وکار تست 1',
        activity_type: 'design_sale',
        created_at_jalali: '1402/01/01',
        details: { amount: 15000 }
      }
    ],
    top_performing_businesses: [
      {
        id: '101',
        name: 'کسب‌وکار تست 1',
        logo: null,
        order_count: 25,
        total_sales: 450000
      },
      {
        id: '102',
        name: 'کسب‌وکار تست 2',
        logo: null,
        order_count: 15,
        total_sales: 300000
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    axiosInstance.get.mockImplementation(() => new Promise(() => {}));
    
    render(<BusinessDetailWidget />, { wrapper: WrapperComponent });
    
    expect(screen.getByText('در حال بارگذاری اطلاعات کسب‌وکار...')).toBeInTheDocument();
  });

  test('renders business data when API call succeeds', async () => {
    axiosInstance.get.mockResolvedValue({ data: mockData });
    
    render(<BusinessDetailWidget />, { wrapper: WrapperComponent });
    
    await waitFor(() => {
      expect(screen.getByText('اطلاعات کسب‌وکارها')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument(); // کسب‌وکارهای فعال
      expect(screen.getByText('10')).toBeInTheDocument(); // کل کسب‌وکارها
      expect(screen.getByText('کسب‌وکار تست 1')).toBeInTheDocument(); // نام کسب‌وکار برتر
      expect(screen.getByText('450,000 تومان')).toBeInTheDocument(); // فروش کسب‌وکار برتر
    });
    
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/dashboard/business-detail/?days=30');
  });

  test('shows error toast when API call fails', async () => {
    const errorMessage = 'خطا در دریافت اطلاعات';
    axiosInstance.get.mockRejectedValue({ message: errorMessage });
    
    render(<BusinessDetailWidget />, { wrapper: WrapperComponent });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری جزئیات کسب‌وکار');
    });
  });

  test('renders fallback UI when no data is available', async () => {
    axiosInstance.get.mockResolvedValue({ data: null });
    
    render(<BusinessDetailWidget />, { wrapper: WrapperComponent });
    
    await waitFor(() => {
      expect(screen.getByText('اطلاعات کسب‌وکار موجود نیست')).toBeInTheDocument();
    });
  });
}); 