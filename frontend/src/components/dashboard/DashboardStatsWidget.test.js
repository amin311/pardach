import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardStatsWidget from './DashboardStatsWidget';

describe('DashboardStatsWidget Component', () => {
  const mockStats = [
    { title: 'سفارش‌ها', value: 120, icon: 'shopping-cart', color: 'blue', suffix: '' },
    { title: 'مجموع فروش', value: 5000000, icon: 'money-bill-wave', color: 'green', suffix: ' تومان' },
    { title: 'پرداخت‌ها', value: 95, icon: 'credit-card', color: 'purple', suffix: '' },
    { title: 'اعلانات جدید', value: 12, icon: 'bell', color: 'yellow', suffix: '' }
  ];

  test('نمایش تمام آیتم‌های آماری', () => {
    render(<DashboardStatsWidget stats={mockStats} />);
    
    // بررسی وجود تمام عناوین
    expect(screen.getByText('سفارش‌ها')).toBeInTheDocument();
    expect(screen.getByText('مجموع فروش')).toBeInTheDocument();
    expect(screen.getByText('پرداخت‌ها')).toBeInTheDocument();
    expect(screen.getByText('اعلانات جدید')).toBeInTheDocument();
    
    // بررسی وجود مقادیر
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('5,000,000 تومان')).toBeInTheDocument();
    expect(screen.getByText('95')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });
  
  test('نمایش آیتم‌های آماری با ساختار صحیح گرید', () => {
    render(<DashboardStatsWidget stats={mockStats} />);
    
    // بررسی ساختار گرید
    const gridContainer = screen.getByTestId('stats-grid');
    expect(gridContainer).toHaveClass('grid');
    expect(gridContainer.childElementCount).toBe(mockStats.length);
  });
  
  test('نمایش پیش‌فرض زمانی که آماری وجود ندارد', () => {
    render(<DashboardStatsWidget stats={[]} />);
    
    // بررسی نمایش پیام عدم وجود آمار
    expect(screen.getByText('آماری برای نمایش وجود ندارد')).toBeInTheDocument();
  });
  
  test('نمایش آیکون‌ها برای هر آیتم آماری', () => {
    render(<DashboardStatsWidget stats={mockStats} />);
    
    // بررسی وجود آیکون‌ها
    const iconContainers = document.querySelectorAll('.rounded-full');
    expect(iconContainers.length).toBe(mockStats.length);
  });
  
  test('نمایش رنگ‌های مختلف برای هر آیتم', () => {
    render(<DashboardStatsWidget stats={mockStats} />);
    
    // بررسی کلاس‌های رنگ برای آیتم‌ها
    expect(document.querySelector('.from-blue-500')).toBeInTheDocument();
    expect(document.querySelector('.from-green-500')).toBeInTheDocument();
    expect(document.querySelector('.from-purple-500')).toBeInTheDocument();
    expect(document.querySelector('.from-yellow-500')).toBeInTheDocument();
  });
  
  test('فرمت اعداد فارسی با جداکننده هزارگان', () => {
    render(<DashboardStatsWidget stats={mockStats} />);
    
    // بررسی فرمت‌دهی صحیح اعداد
    expect(screen.getByText('5,000,000 تومان')).toBeInTheDocument();
  });
}); 