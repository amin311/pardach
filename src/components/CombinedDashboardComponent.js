import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axiosInstance from '../lib/axios';
import { toast } from 'react-toastify';

// کامپوننت‌های داشبورد
import DashboardWidget from './dashboard/DashboardWidget';
import SalesDetailWidget from './dashboard/SalesDetailWidget';
import BusinessDetailWidget from './dashboard/BusinessDetailWidget';

// کامپوننت‌های صفحه اصلی
import WelcomeSection from './main/WelcomeSection';
import NotificationWidget from './main/NotificationWidget';
import NavigationMenuWidget from './main/NavigationMenuWidget';
import PromotionalSlider from './main/PromotionalSlider';

const CombinedDashboardComponent = ({ userId, isAdmin = false }) => {
  const [combinedData, setCombinedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCombinedData();
  }, [userId, isAdmin]);

  const fetchCombinedData = async () => {
    try {
      const response = await axiosInstance.get('/api/dashboard/combined/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setCombinedData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching combined data:', error);
      setError('خطا در بارگذاری اطلاعات یکپارچه');
      toast.error('خطا در بارگذاری اطلاعات یکپارچه');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 animate-pulse">
        <div className="h-8 w-1/3 bg-gray-200 rounded mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error && !combinedData) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <i className="fas fa-exclamation-triangle text-red-500"></i> خطا
        </h2>
        <div className="text-center py-6">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={fetchCombinedData}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="p-6"
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-800 border-r-4 border-blue-500 pr-3">
        داشبورد یکپارچه
      </h2>
      
      {/* بخش خوش‌آمدگویی */}
      {combinedData?.main?.welcomeData && (
        <div className="mb-6">
          <WelcomeSection 
            userData={combinedData.main.welcomeData}
            useCombinedData={true}
          />
        </div>
      )}
      
      {/* اسلایدر تبلیغاتی */}
      {combinedData?.main?.promotionalItems && combinedData.main.promotionalItems.length > 0 && (
        <div className="mb-6">
          <PromotionalSlider 
            items={combinedData.main.promotionalItems}
            useCombinedData={true} 
          />
        </div>
      )}
      
      {/* منوی ناوبری */}
      {combinedData?.main?.navigationMenu && (
        <div className="mb-8">
          <NavigationMenuWidget 
            menuItems={combinedData.main.navigationMenu}
            userRole={isAdmin ? 'admin' : 'user'}
            useCombinedData={true}
          />
        </div>
      )}
      
      {/* خلاصه داشبورد */}
      <div className="mb-8">
        <DashboardWidget 
          userId={userId} 
          isAdmin={isAdmin} 
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* جزئیات فروش */}
        <SalesDetailWidget 
          days={30} 
          useCombinedApi={true} 
        />
        
        {/* جزئیات کسب و کار */}
        <BusinessDetailWidget 
          days={30} 
          useCombinedApi={true} 
        />
      </div>
      
      {/* اعلان‌ها */}
      {combinedData?.main?.notifications && (
        <div className="mb-8">
          <NotificationWidget 
            notifications={combinedData.main.notifications}
            useCombinedData={true}
          />
        </div>
      )}
      
      <div className="text-center mt-8 text-sm text-gray-500">
        <p>داده‌های نمایش داده شده از طریق API یکپارچه دریافت شده‌اند</p>
      </div>
    </motion.div>
  );
};

export default CombinedDashboardComponent; 