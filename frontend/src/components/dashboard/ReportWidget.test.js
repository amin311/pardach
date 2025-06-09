import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import ReportWidget from './ReportWidget';

// Mock axios
jest.mock('axios');

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  },
}));

// Mock reports data
const mockReports = [
  {
    id: '1',
    title: 'گزارش فروش ماهانه',
    type: 'sales',
    status: 'completed',
    created_at_jalali: '1402/02/15',
    user: {
      id: '1',
      username: 'admin',
    }
  },
  {
    id: '2',
    title: 'گزارش موجودی انبار',
    type: 'inventory',
    status: 'processing',
    created_at_jalali: '1402/02/14',
    user: {
      id: '2',
      username: 'user1',
    }
  },
];

const WrapperComponent = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('ReportWidget Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', async () => {
    // Arrange
    axiosInstance.get.mockImplementation(() => new Promise(() => {})); // Never resolves

    // Act
    render(<ReportWidget />, { wrapper: WrapperComponent });

    // Assert
    expect(screen.getByText('در حال بارگذاری گزارش‌ها...')).toBeInTheDocument();
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/reports/?limit=5');
  });

  it('should render reports when API call succeeds', async () => {
    // Arrange
    axiosInstance.get.mockResolvedValue({ data: mockReports });

    // Act
    render(<ReportWidget />, { wrapper: WrapperComponent });

    // Assert
    await waitFor(() => {
      expect(screen.getByText('گزارش‌های اخیر')).toBeInTheDocument();
      expect(screen.getByText('گزارش فروش ماهانه')).toBeInTheDocument();
      expect(screen.getByText('گزارش موجودی انبار')).toBeInTheDocument();
      expect(screen.getByText('1402/02/15')).toBeInTheDocument();
      expect(screen.getByText('admin')).toBeInTheDocument();
    });
  });

  it('should show error toast when API call fails', async () => {
    // Arrange
    axiosInstance.get.mockRejectedValue(new Error('Network Error'));

    // Act
    render(<ReportWidget />, { wrapper: WrapperComponent });

    // Assert
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('خطا در بارگذاری گزارش‌ها');
    });
  });

  it('should render message when no reports are found', async () => {
    // Arrange
    axiosInstance.get.mockResolvedValue({ data: [] });

    // Act
    render(<ReportWidget />, { wrapper: WrapperComponent });

    // Assert
    await waitFor(() => {
      expect(screen.getByText('گزارش‌های اخیر')).toBeInTheDocument();
      expect(screen.getByText('گزارشی یافت نشد')).toBeInTheDocument();
    });
  });
}); 