import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DashboardChartWidget from './DashboardChartWidget';

// موک کردن Chart.js
jest.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="bar-chart">نمودار ستونی</div>,
  Line: () => <div data-testid="line-chart">نمودار خطی</div>,
  Pie: () => <div data-testid="pie-chart">نمودار دایره‌ای</div>,
}));

describe('DashboardChartWidget Component', () => {
  const mockProps = {
    title: 'آمار فروش',
    type: 'bar',
    data: {
      labels: ['فروردین', 'اردیبهشت', 'خرداد'],
      datasets: [
        {
          label: 'فروش',
          data: [12, 19, 3],
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
      },
    },
    description: 'نمایش میزان فروش ماهانه',
    icon: 'chart-bar',
    color: 'blue'
  };

  test('نمایش عنوان نمودار', () => {
    render(<DashboardChartWidget {...mockProps} />);
    
    expect(screen.getByText('آمار فروش')).toBeInTheDocument();
  });

  test('نمایش توضیحات نمودار', () => {
    render(<DashboardChartWidget {...mockProps} />);
    
    expect(screen.getByText('نمایش میزان فروش ماهانه')).toBeInTheDocument();
  });

  test('نمایش نمودار ستونی', () => {
    render(<DashboardChartWidget {...mockProps} />);
    
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  test('نمایش نمودار خطی', () => {
    render(<DashboardChartWidget {...mockProps} type="line" />);
    
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  test('نمایش نمودار دایره‌ای', () => {
    render(<DashboardChartWidget {...mockProps} type="pie" />);
    
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  test('نمایش نمودار پیش‌فرض برای نوع نامعتبر', () => {
    render(<DashboardChartWidget {...mockProps} type="invalid" />);
    
    // در صورت نوع نامعتبر، باید نمودار ستونی نمایش داده شود
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  test('نمایش کلاس رنگ مناسب', () => {
    render(<DashboardChartWidget {...mockProps} color="blue" />);
    
    const header = screen.getByText('آمار فروش').closest('div');
    expect(header).toHaveClass('text-blue-600');
  });

  test('نمایش آیکون مناسب', () => {
    render(<DashboardChartWidget {...mockProps} icon="chart-bar" />);
    
    // بررسی وجود کلاس آیکون
    const iconElement = document.querySelector('.fas.fa-chart-bar');
    expect(iconElement).toBeInTheDocument();
  });

  test('امکان تغییر نوع نمودار', () => {
    render(<DashboardChartWidget {...mockProps} />);
    
    // ابتدا نمودار ستونی نمایش داده می‌شود
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    
    // کلیک روی دکمه تغییر به نمودار خطی
    fireEvent.click(screen.getByText('خطی'));
    
    // اکنون باید نمودار خطی نمایش داده شود
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    
    // کلیک روی دکمه تغییر به نمودار دایره‌ای
    fireEvent.click(screen.getByText('دایره‌ای'));
    
    // اکنون باید نمودار دایره‌ای نمایش داده شود
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });
}); 