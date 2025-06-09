import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

// ثبت کامپوننت‌های موردنیاز ChartJS
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

const SalesDetailWidget = ({ days = 30, useCombinedApi = true }) => {
  const [salesData, setSalesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSalesData();
  }, [days]);

  const fetchSalesData = async () => {
    try {
      // استفاده از API یکپارچه اگر فعال باشد
      if (useCombinedApi) {
        const response = await axiosInstance.get(`/api/dashboard/combined/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        // فقط بخش chart مرتبط با فروش را استفاده می‌کنیم
        const orderChart = response.data.dashboard.charts.find(chart => chart.title === 'آمار سفارش‌ها');
        
        setSalesData({
          total_orders: response.data.dashboard.summary.order_count || 0,
          total_sales: response.data.dashboard.summary.total_sales || 0,
          sales_trend: orderChart || {
            labels: [],
            values: [],
            type: 'line'
          }
        });
      } else {
        // استفاده از API فرعی اختصاصی فروش
        const response = await axiosInstance.get(`/api/dashboard/sales/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setSalesData(response.data);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching sales data:', error);
      setError('خطا در بارگذاری اطلاعات فروش');
      toast.error('خطا در بارگذاری اطلاعات فروش');
      setLoading(false);
      
      // تلاش برای استفاده از API قبلی در صورت خطا
      try {
        const fallbackResponse = await axiosInstance.get(`/api/dashboard/sales/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setSalesData(fallbackResponse.data);
      } catch (fallbackError) {
        console.error('Error in fallback sales API:', fallbackError);
      }
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  // تنظیمات نمودار
  const getChartData = () => {
    if (!salesData || !salesData.sales_trend || !salesData.sales_trend.labels) return null;
    
    return {
      labels: salesData.sales_trend.labels,
      datasets: [
        {
          label: 'فروش',
          data: salesData.sales_trend.values,
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
          tension: 0.3,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Vazir, Tahoma, sans-serif'
          }
        }
      },
      title: {
        display: true,
        text: 'روند فروش',
        font: {
          family: 'Vazir, Tahoma, sans-serif',
          size: 16
        }
      },
      tooltip: {
        titleFont: {
          family: 'Vazir, Tahoma, sans-serif'
        },
        bodyFont: {
          family: 'Vazir, Tahoma, sans-serif'
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          font: {
            family: 'Vazir, Tahoma, sans-serif'
          },
          callback: function(value) {
            return formatNumber(value) + ' تومان';
          }
        }
      },
      x: {
        ticks: {
          font: {
            family: 'Vazir, Tahoma, sans-serif'
          }
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md animate-pulse">
        <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
        <div className="h-48 bg-gray-200 rounded mb-4"></div>
        <div className="grid grid-cols-3 gap-4">
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
          <i className="fas fa-chart-line text-blue-500"></i> آمار فروش
        </h3>
        <div className="text-center py-4">
          <p className="text-red-500">{error}</p>
          <button
            onClick={fetchSalesData}
            className="mt-2 text-blue-500 hover:text-blue-700"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  if (!salesData) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-4 bg-white rounded-lg shadow-md"
    >
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <i className="fas fa-chart-line text-blue-500"></i> آمار فروش
      </h3>
      
      {/* نمودار روند فروش */}
      <div className="h-64 mb-6">
        {getChartData() ? (
          <Line data={getChartData()} options={chartOptions} />
        ) : (
          <div className="h-full flex items-center justify-center">
            <p className="text-gray-500">داده‌ای برای نمایش وجود ندارد</p>
          </div>
        )}
      </div>
      
      {/* آمار کلی */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">کل سفارش‌ها</p>
          <p className="text-xl font-bold">{formatNumber(salesData.total_orders || 0)}</p>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">مجموع فروش</p>
          <p className="text-xl font-bold">{formatNumber(salesData.total_sales || 0)}<span className="text-xs mr-1">تومان</span></p>
        </div>
      </div>
      
      {/* محصولات پرفروش (اگر در API موجود باشد) */}
      {salesData.top_products && salesData.top_products.length > 0 && (
        <div className="mt-6">
          <h4 className="text-md font-medium mb-2">محصولات پرفروش</h4>
          <div className="space-y-2">
            {salesData.top_products.map((product, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span>{product.name}</span>
                <span className="text-sm text-gray-500">{formatNumber(product.count)} فروش</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 text-center">
        <Link to="/dashboard" className="text-blue-500 hover:underline text-sm">
          مشاهده گزارش کامل فروش
        </Link>
      </div>
    </motion.div>
  );
};

export default SalesDetailWidget; 