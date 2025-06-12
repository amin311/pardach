import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import MainPage from './MainPage';

// Mock axios
jest.mock('axios');

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  },
}));

// Mock react-slick
jest.mock('react-slick', () => ({ children }) => <div data-testid="slick-slider">{children}</div>);

// Mock the components
jest.mock('../../components/main/WelcomeSection', () => () => <div data-testid="welcome-section">Welcome Section</div>);
jest.mock('../../components/main/PromotionalSlider', () => () => <div data-testid="promo-slider">Promo Slider</div>);
jest.mock('../../components/main/NavigationMenuWidget', () => () => <div data-testid="nav-menu">Navigation Menu</div>);
jest.mock('../../components/main/NotificationWidget', () => () => <div data-testid="notification-widget">Notifications</div>);
jest.mock('../../components/main/DashboardWidget', () => () => <div data-testid="dashboard-widget">Dashboard</div>);
jest.mock('../../components/main/RecentOrdersWidget', () => () => <div data-testid="orders-widget">Recent Orders</div>);
jest.mock('../../components/main/InteractiveGuide', () => ({ userId, hasSeenGuide }) => (
  <div data-testid="interactive-guide" data-user-id={userId} data-has-seen-guide={hasSeenGuide ? 'true' : 'false'}>
    Interactive Guide
  </div>
));

// Mock MainPage data
const mockMainPageData = {
  welcome_data: {
    first_name: 'علی',
    last_name: 'محمدی',
    unread_count: 2,
    order_in_progress: 1,
  },
  summary: {
    order_count: 5,
    payment_count: 3,
    unread_notifications: 2,
    recent_orders: [{ id: '1', total_price: 10000, status: 'pending' }],
    recent_notifications: [{ id: '1', title: 'تست', read: false }],
  },
  promotions: [
    { id: 1, title: 'طرح‌های جدید', image: '/static/images/promo1.jpg', link: '/designs' },
  ],
  navigation: [
    { title: 'طرح‌ها', icon: 'fa-paint-brush', link: '/designs', visible: true },
    { title: 'سفارش‌ها', icon: 'fa-shopping-cart', link: '/orders', visible: true },
  ],
};

describe('صفحه اصلی برنامه', () => {
  // قبل از هر تست
  beforeEach(() => {
    localStorage.setItem('access_token', 'test-token');
    
    // تنظیم دسترسی به localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(key => key === 'access_token' ? 'test-token' : null),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true
    });
    
    // موک کردن API درخواست‌ها
    axiosInstance.get.mockImplementation((url) => {
      if (url === '/api/auth/user-info/') {
        return Promise.resolve({ data: { id: 1, is_staff: false, is_superuser: false } });
      }
      if (url === '/api/main/page-summary/') {
        return Promise.resolve({ data: mockMainPageData });
      }
      if (url === '/api/main/settings/') {
        return Promise.resolve({ data: [
          { key: 'user_1_has_seen_guide', value: 'true' }
        ]});
      }
      return Promise.reject(new Error('Not found'));
    });
  });

  // پس از هر تست
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('باید به درستی بارگذاری شود و همه کامپوننت‌ها را نمایش دهد', async () => {
    render(<MainPage />, { wrapper: MemoryRouter });
    
    // بررسی وضعیت بارگذاری در ابتدا
    await waitFor(() => {
      expect(screen.getByTestId('welcome-section')).toBeInTheDocument();
      expect(screen.getByTestId('promo-slider')).toBeInTheDocument();
      expect(screen.getByTestId('nav-menu')).toBeInTheDocument();
      expect(screen.getByTestId('dashboard-widget')).toBeInTheDocument();
      expect(screen.getByTestId('orders-widget')).toBeInTheDocument();
      expect(screen.getByTestId('notification-widget')).toBeInTheDocument();
      expect(screen.getByTestId('interactive-guide')).toBeInTheDocument();
    });
    
    // بررسی فراخوانی‌های API
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/auth/user-info/', expect.anything());
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/main/page-summary/', expect.anything());
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/main/settings/', expect.anything());
  });

  test('باید در صورت عدم وجود توکن، به صفحه ورود هدایت شود', async () => {
    window.localStorage.getItem.mockReturnValue(null);
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<MainPage />, { wrapper: MemoryRouter });
    
    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith('/login');
    });
  });

  test('باید در صورت خطا، پیام خطا نمایش داده شود', async () => {
    axiosInstance.get.mockImplementation((url) => {
      if (url === '/api/auth/user-info/') {
        return Promise.resolve({ data: { id: 1, is_staff: false } });
      }
      if (url === '/api/main/page-summary/') {
        return Promise.reject(new Error('API error'));
      }
      return Promise.reject(new Error('Not found'));
    });
    
    render(<MainPage />, { wrapper: MemoryRouter });
    
    // بررسی نمایش پیام خطا
    await waitFor(() => {
      expect(screen.getByText(/خطا/i)).toBeInTheDocument();
      expect(screen.getByText(/تلاش مجدد/i)).toBeInTheDocument();
      expect(toast.error).toHaveBeenCalled();
    });
  });
  
  test('باید راهنما را برای کاربری که قبلاً ندیده است نمایش دهد', async () => {
    // موک کردن عدم وجود تنظیمات راهنما
    axiosInstance.get.mockImplementation((url) => {
      if (url === '/api/auth/user-info/') {
        return Promise.resolve({ data: { id: 1, is_staff: false } });
      }
      if (url === '/api/main/page-summary/') {
        return Promise.resolve({ data: mockMainPageData });
      }
      if (url === '/api/main/settings/') {
        return Promise.resolve({ data: [] }); // هیچ تنظیمی برای راهنما وجود ندارد
      }
      return Promise.reject(new Error('Not found'));
    });
    
    render(<MainPage />, { wrapper: MemoryRouter });
    
    // بررسی نمایش راهنما
    await waitFor(() => {
      const guide = screen.getByTestId('interactive-guide');
      expect(guide).toBeInTheDocument();
      expect(guide.dataset.hasSeenGuide).toBe('false');
    });
  });
  
  test('باید راهنما را برای کاربری که قبلاً دیده است نمایش ندهد', async () => {
    // موک کردن وجود تنظیمات راهنما
    axiosInstance.get.mockImplementation((url) => {
      if (url === '/api/auth/user-info/') {
        return Promise.resolve({ data: { id: 1, is_staff: false } });
      }
      if (url === '/api/main/page-summary/') {
        return Promise.resolve({ data: mockMainPageData });
      }
      if (url === '/api/main/settings/') {
        return Promise.resolve({ data: [
          { key: 'user_1_has_seen_guide', value: 'true' }
        ]});
      }
      return Promise.reject(new Error('Not found'));
    });
    
    render(<MainPage />, { wrapper: MemoryRouter });
    
    // بررسی نمایش راهنما
    await waitFor(() => {
      const guide = screen.getByTestId('interactive-guide');
      expect(guide).toBeInTheDocument();
      expect(guide.dataset.hasSeenGuide).toBe('true');
    });
  });
}); 