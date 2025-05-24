import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

const BusinessDetailWidget = ({ days = 30, useCombinedApi = true }) => {
  const [businessData, setBusinessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBusinessData();
  }, [days]);

  const fetchBusinessData = async () => {
    try {
      // استفاده از API یکپارچه اگر فعال باشد
      if (useCombinedApi) {
        const response = await axios.get(`/api/dashboard/combined/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        // استخراج اطلاعات کسب و کار از پاسخ یکپارچه
        setBusinessData({
          active_businesses: response.data.dashboard.summary.active_businesses || 0,
          total_businesses: response.data.dashboard.summary.total_businesses || 0,
          recent_activities: response.data.main?.businessActivities || [],
          top_businesses: response.data.dashboard.topBusinesses || []
        });
      } else {
        // استفاده از API جداگانه کسب و کار
        const response = await axios.get(`/api/dashboard/business/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setBusinessData(response.data);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching business data:', error);
      setError('خطا در بارگذاری اطلاعات کسب و کار');
      toast.error('خطا در بارگذاری اطلاعات کسب و کار');
      setLoading(false);
      
      // تلاش برای استفاده از API قبلی در صورت خطا
      try {
        const fallbackResponse = await axios.get(`/api/dashboard/business/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setBusinessData(fallbackResponse.data);
      } catch (fallbackError) {
        console.error('Error in fallback business API:', fallbackError);
      }
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  if (loading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md animate-pulse">
        <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded mb-3"></div>
        <div className="h-20 bg-gray-200 rounded mb-4"></div>
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
          <i className="fas fa-building text-purple-500"></i> کسب و کارها
        </h3>
        <div className="text-center py-4">
          <p className="text-red-500">{error}</p>
          <button
            onClick={fetchBusinessData}
            className="mt-2 text-blue-500 hover:text-blue-700"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  if (!businessData) {
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
        <i className="fas fa-building text-purple-500"></i> کسب و کارها
      </h3>
      
      {/* آمار کلی کسب و کارها */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-purple-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">کسب و کارهای فعال</p>
          <p className="text-xl font-bold">{formatNumber(businessData.active_businesses || 0)}</p>
        </div>
        
        <div className="bg-indigo-50 p-3 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">کل کسب و کارها</p>
          <p className="text-xl font-bold">{formatNumber(businessData.total_businesses || 0)}</p>
        </div>
      </div>
      
      {/* فعالیت‌های اخیر */}
      {businessData.recent_activities && businessData.recent_activities.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium mb-2">فعالیت‌های اخیر</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto pr-1 scrollbar-thin">
            {businessData.recent_activities.map((activity, index) => (
              <div key={index} className="p-2 bg-gray-50 rounded text-sm">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{activity.business_name}</span>
                  <span className="text-xs text-gray-500">{formatDate(activity.date)}</span>
                </div>
                <p className="text-gray-700 mt-1">{activity.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* کسب و کارهای برتر */}
      {businessData.top_businesses && businessData.top_businesses.length > 0 && (
        <div>
          <h4 className="text-md font-medium mb-2">کسب و کارهای برتر</h4>
          <div className="space-y-2">
            {businessData.top_businesses.map((business, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{business.name}</span>
                  {business.category && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded mr-2">
                      {business.category}
                    </span>
                  )}
                </div>
                <Link 
                  to={`/businesses/${business.id}`} 
                  className="text-xs text-blue-500 hover:underline"
                >
                  جزئیات
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 text-center">
        <Link to="/businesses" className="text-blue-500 hover:underline text-sm">
          مشاهده همه کسب و کارها
        </Link>
      </div>
    </motion.div>
  );
};

export default BusinessDetailWidget; 