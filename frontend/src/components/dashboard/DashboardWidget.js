import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

const DashboardWidget = ({ userId, isAdmin }) => {
  const [summaryData, setSummaryData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummaryData();
  }, []);

  const fetchSummaryData = async () => {
    try {
      // استفاده از API یکپارچه جدید برای افزایش کارایی
      const response = await axiosInstance.get('/api/dashboard/combined/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      // استخراج داده‌های داشبورد از نتیجه یکپارچه
      setSummaryData(response.data.dashboard.summary);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('خطا در بارگذاری اطلاعات داشبورد');
      toast.error('خطا در بارگذاری اطلاعات داشبورد');
      setLoading(false);

      // در صورت خطا، تلاش برای استفاده از API قبلی
      try {
        const fallbackResponse = await axiosInstance.get('/api/dashboard/summary/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setSummaryData(fallbackResponse.data.summary);
      } catch (fallbackError) {
        console.error('Error in fallback dashboard API:', fallbackError);
      }
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  if (loading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md animate-pulse">
        <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
        <div className="grid grid-cols-2 gap-4">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
          <i className="fas fa-tachometer-alt text-blue-500"></i> خلاصه داشبورد
        </h3>
        <div className="text-center py-4">
          <p className="text-red-500">{error}</p>
          <button
            onClick={fetchSummaryData}
            className="mt-2 text-blue-500 hover:text-blue-700"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-4 bg-white rounded-lg shadow-md"
    >
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <i className="fas fa-tachometer-alt text-blue-500"></i> خلاصه داشبورد
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">کل سفارشات</p>
          <p className="text-xl font-bold">{formatNumber(summaryData.order_count || 0)}</p>
          <p className="text-sm text-blue-500">{formatNumber(summaryData.total_sales || 0)} تومان</p>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">پرداخت‌ها</p>
          <p className="text-xl font-bold">{formatNumber(summaryData.payment_count || 0)}</p>
          <p className="text-sm text-green-500">{formatNumber(summaryData.total_payments || 0)} تومان</p>
        </div>
        
        <div className="bg-red-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">اعلانات خوانده نشده</p>
          <p className="text-xl font-bold">{formatNumber(summaryData.unread_notifications || 0)}</p>
        </div>
        
        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">گزارش‌ها</p>
          <p className="text-xl font-bold">{formatNumber(summaryData.report_count || 0)}</p>
        </div>
        
        {/* نمایش تعداد کسب‌وکارها در صورت وجود */}
        {summaryData.business_count !== undefined && (
          <div className="bg-yellow-50 p-3 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">کل کسب‌وکارها</p>
            <p className="text-xl font-bold">{formatNumber(summaryData.business_count || 0)}</p>
            <p className="text-sm text-yellow-600">
              {formatNumber(summaryData.active_business_count || 0)} فعال
            </p>
          </div>
        )}
      </div>
      
      <div className="mt-3 text-center">
        <Link to="/dashboard" className="text-blue-500 hover:underline text-sm">
          مشاهده کامل داشبورد
        </Link>
      </div>
    </motion.div>
  );
};

export default DashboardWidget; 