import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { FaHome, FaUser, FaCalendarAlt, FaClock } from 'react-icons/fa';

/**
 * کامپوننت بخش خوش‌آمدگویی که به کاربر خوش‌آمد می‌گوید
 * @param {Object} userData - اطلاعات کاربر (نام، تصویر و غیره)
 */
const WelcomeSection = ({ userData }) => {
  // تعیین پیام خوش‌آمدگویی متناسب با زمان روز
  const welcomeMessage = useMemo(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      return 'صبح بخیر';
    } else if (hour >= 12 && hour < 17) {
      return 'ظهر بخیر';
    } else if (hour >= 17 && hour < 21) {
      return 'عصر بخیر';
    } else {
      return 'شب بخیر';
    }
  }, []);

  // تعیین رنگ متناسب با زمان روز
  const timeBasedColor = useMemo(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      return 'from-yellow-300 to-orange-400'; // صبح
    } else if (hour >= 12 && hour < 17) {
      return 'from-blue-400 to-cyan-500'; // ظهر
    } else if (hour >= 17 && hour < 21) {
      return 'from-orange-400 to-red-500'; // عصر
    } else {
      return 'from-indigo-600 to-purple-600'; // شب
    }
  }, []);

  // تبدیل تاریخ به فرمت فارسی
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

  // نام کامل یا نام کاربری
  const displayName = userData.full_name || userData.username;

  return (
    <motion.div 
      className="bg-white rounded-lg shadow-md overflow-hidden"
      whileHover={{ scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className={`bg-gradient-to-r ${timeBasedColor} p-6 text-white`}>
        <h1 className="text-3xl font-bold rtl">
          {welcomeMessage}{userData?.first_name ? ` ${userData.first_name} عزیز` : ''}!
        </h1>
        <p className="mt-2 opacity-90">
          {userData?.last_login 
            ? `آخرین ورود شما: ${userData.last_login_jalali}`
            : 'به سیستم مدیریت چاپ و طرح خوش آمدید'
          }
        </p>
      </div>

      <div className="p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="bg-gray-100 p-2 px-4 rounded-full text-sm">
            <span className="font-semibold">امروز:</span> {userData?.today_date_jalali || 'تاریخ نامشخص'}
          </div>
          
          {userData?.unread_count > 0 && (
            <div className="bg-red-100 text-red-700 p-2 px-4 rounded-full text-sm">
              <span className="font-semibold">{userData.unread_count}</span> پیام خوانده نشده
            </div>
          )}
          
          {userData?.order_in_progress > 0 && (
            <div className="bg-blue-100 text-blue-700 p-2 px-4 rounded-full text-sm">
              <span className="font-semibold">{userData.order_in_progress}</span> سفارش در حال پیگیری
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default WelcomeSection; 