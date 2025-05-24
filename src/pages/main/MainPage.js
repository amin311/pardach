import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

// کامپوننت‌های لازم برای صفحه اصلی
import WelcomeSection from '../../components/main/WelcomeSection';
import PromotionalSlider from '../../components/main/PromotionalSlider';
import NavigationMenuWidget from '../../components/main/NavigationMenuWidget';
import NotificationWidget from '../../components/main/NotificationWidget';
import DashboardWidget from '../../components/main/DashboardWidget';
import RecentOrdersWidget from '../../components/main/RecentOrdersWidget';
import InteractiveGuide from '../../components/main/InteractiveGuide';

/**
 * صفحه اصلی (لندینگ پیج) برنامه
 */
const MainPage = () => {
  const [mainData, setMainData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [hasSeenGuide, setHasSeenGuide] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    // بررسی وجود توکن معتبر در لوکال استوریج
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }
    
    // دریافت اطلاعات کاربر و صفحه اصلی
    fetchUserInfo();
    fetchMainPageData();
  }, [navigate]);
  
  // بررسی آیا کاربر قبلا راهنما را دیده است
  useEffect(() => {
    if (userId) {
      checkGuideStatus(userId);
    }
  }, [userId]);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/api/auth/user-info/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setUserId(response.data.id);
      setIsAdmin(response.data.is_staff || response.data.is_superuser);
    } catch (error) {
      console.error('Error fetching user info:', error);
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
      }
    }
  };

  const fetchMainPageData = async () => {
    try {
      const response = await axios.get('/api/main/page-summary/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setMainData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching main page data:', error);
      setError('خطا در بارگذاری اطلاعات صفحه اصلی');
      toast.error('خطا در بارگذاری اطلاعات صفحه اصلی');
      setLoading(false);
      
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
      }
    }
  };
  
  const checkGuideStatus = async (userId) => {
    try {
      const response = await axios.get('/api/main/settings/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      // بررسی آیا تنظیم مربوط به راهنما وجود دارد
      const guideStatus = response.data.find(setting => setting.key === `user_${userId}_has_seen_guide`);
      setHasSeenGuide(guideStatus?.value === 'true');
    } catch (error) {
      console.error('Error checking guide status:', error);
      // در صورت خطا فرض می‌کنیم کاربر راهنما را ندیده است
      setHasSeenGuide(false);
    }
  };

  // نمایش وضعیت بارگذاری
  if (loading) {
    return (
      <div className="container mx-auto p-6 rtl">
        <div className="animate-pulse">
          <div className="h-12 bg-gray-200 rounded-md w-3/4 mb-6"></div>
          <div className="h-40 bg-gray-200 rounded-md mb-8"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="h-24 bg-gray-200 rounded-md"></div>
            <div className="h-24 bg-gray-200 rounded-md"></div>
            <div className="h-24 bg-gray-200 rounded-md"></div>
            <div className="h-24 bg-gray-200 rounded-md"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-80 bg-gray-200 rounded-md"></div>
            <div className="h-80 bg-gray-200 rounded-md"></div>
          </div>
        </div>
      </div>
    );
  }

  // نمایش خطا
  if (error) {
    return (
      <div className="container mx-auto p-6 rtl">
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h2 className="text-xl font-bold mb-4 flex items-center justify-center gap-2">
            <i className="fas fa-exclamation-triangle text-red-500"></i> خطا
          </h2>
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={fetchMainPageData}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto p-6 rtl"
      >
        {/* بخش خوش‌آمدگویی */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-6 welcome-section"
        >
          <WelcomeSection userData={mainData?.welcome_data || {}} />
        </motion.div>
        
        {/* اسلایدر تبلیغاتی */}
        {mainData?.promotions && mainData.promotions.length > 0 && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-8"
          >
            <PromotionalSlider items={mainData.promotions.map(p => ({
              title: p.title,
              description: p.description || '',
              image_url: p.image,
              link: p.link
            }))} />
          </motion.div>
        )}
        
        {/* منوی ناوبری */}
        {mainData?.navigation && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-10 nav-menu-widget"
          >
            <NavigationMenuWidget 
              menuItems={mainData.navigation} 
              userRole={isAdmin ? 'admin' : 'user'}
            />
          </motion.div>
        )}
        
        {/* ویجت خلاصه داشبورد */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-8 dashboard-widget"
        >
          <DashboardWidget userId={userId} isAdmin={isAdmin} />
        </motion.div>
        
        {/* ویجت‌های سفارش و اعلانات */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
        >
          <div className="orders-widget">
            <RecentOrdersWidget orders={mainData?.summary?.recent_orders || []} />
          </div>
          <div className="notification-widget">
            <NotificationWidget notifications={mainData?.summary?.recent_notifications || []} />
          </div>
        </motion.div>
      </motion.div>
      
      {/* راهنمای تعاملی */}
      {userId && <InteractiveGuide userId={userId} hasSeenGuide={hasSeenGuide} />}
    </>
  );
};

export default MainPage; 