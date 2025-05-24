import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const DetailNotification = ({ userId, isAdmin }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [notification, setNotification] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotificationDetails();
  }, [id]);

  // دریافت جزئیات اعلان
  const fetchNotificationDetails = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`/api/notification/${id}/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setNotification(response.data);
      setLoading(false);
    } catch (error) {
      console.error('خطا در دریافت جزئیات اعلان:', error);
      
      if (error.response && error.response.status === 404) {
        toast.error('اعلان مورد نظر یافت نشد');
        navigate('/notifications');
      } else {
        toast.error('خطا در بارگذاری جزئیات اعلان');
      }
      
      setLoading(false);
    }
  };

  // علامت‌گذاری اعلان به عنوان خوانده‌شده
  const markAsRead = async () => {
    try {
      await axios.post(`/api/notification/${id}/read/`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setNotification(prev => ({ ...prev, is_read: true }));
      toast.success('اعلان خوانده شد');
    } catch (error) {
      console.error('خطا در علامت‌گذاری اعلان:', error);
      toast.error('خطا در علامت‌گذاری اعلان');
    }
  };

  // آرشیو کردن اعلان
  const archiveNotification = async () => {
    try {
      await axios.post(`/api/notification/${id}/archive/`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setNotification(prev => ({ ...prev, is_archived: true }));
      toast.success('اعلان آرشیو شد');
    } catch (error) {
      console.error('خطا در آرشیو کردن اعلان:', error);
      toast.error('خطا در آرشیو کردن اعلان');
    }
  };

  // آیکون مناسب برای هر نوع اعلان
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'order_status':
        return <i className="fas fa-shopping-cart text-blue-500 text-3xl"></i>;
      case 'payment_status':
        return <i className="fas fa-money-bill-wave text-green-500 text-3xl"></i>;
      case 'business_activity':
        return <i className="fas fa-briefcase text-purple-500 text-3xl"></i>;
      case 'system':
        return <i className="fas fa-cog text-red-500 text-3xl"></i>;
      case 'user':
        return <i className="fas fa-user text-orange-500 text-3xl"></i>;
      default:
        return <i className="fas fa-bell text-gray-500 text-3xl"></i>;
    }
  };

  // لیبل فارسی برای نوع اعلان
  const getTypeLabel = (type) => {
    const typeLabels = {
      'order_status': 'وضعیت سفارش',
      'payment_status': 'وضعیت پرداخت',
      'business_activity': 'فعالیت کسب‌وکار',
      'system': 'سیستمی',
      'user': 'کاربری'
    };
    
    return typeLabels[type] || type;
  };

  if (loading) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
            <div className="h-10 bg-gray-200 rounded w-1/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!notification) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-10 text-center">
          <i className="fas fa-exclamation-circle text-red-500 text-5xl mb-4"></i>
          <p className="text-gray-500 text-lg">اعلان مورد نظر یافت نشد</p>
          <Link to="/notifications" className="mt-4 inline-block text-blue-500 hover:text-blue-700">
            بازگشت به لیست اعلانات
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white rounded-lg shadow-md overflow-hidden"
      >
        <div className="bg-gray-50 p-4 border-b flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <i className="fas fa-bell text-blue-500"></i> جزئیات اعلان
          </h2>
          
          <Link to="/notifications" className="text-gray-500 hover:text-gray-700">
            <i className="fas fa-arrow-right ml-1"></i> بازگشت به لیست
          </Link>
        </div>
        
        <div className="p-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="md:w-1/5 flex flex-col items-center">
              <div className={`p-6 rounded-full ${notification.is_read ? 'bg-gray-100' : 'bg-blue-100'} mb-4`}>
                {getNotificationIcon(notification.type)}
              </div>
              
              <span className={`px-3 py-1 rounded-full text-sm text-center ${
                notification.is_read ? 'bg-gray-200' : 'bg-blue-500 text-white'
              }`}>
                {notification.is_read ? 'خوانده شده' : 'خوانده نشده'}
              </span>
              
              <span className={`mt-2 px-3 py-1 rounded-full text-sm text-center ${
                notification.is_archived ? 'bg-yellow-200' : 'bg-gray-200'
              }`}>
                {notification.is_archived ? 'آرشیو شده' : 'آرشیو نشده'}
              </span>
            </div>
            
            <div className="md:w-4/5">
              <h1 className="text-2xl font-bold mb-4">{notification.title}</h1>
              
              <div className="mb-6">
                <p className="text-gray-700 whitespace-pre-line leading-7">{notification.content}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-500">نوع اعلان</p>
                  <p className="font-medium">{getTypeLabel(notification.type)}</p>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-500">اولویت</p>
                  <p className="font-medium">{notification.priority}</p>
                </div>
                
                {notification.category && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">دسته‌بندی</p>
                    <p className="font-medium">{notification.category.name}</p>
                  </div>
                )}
                
                {notification.business && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">کسب‌وکار</p>
                    <p className="font-medium">{notification.business.name}</p>
                  </div>
                )}
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-500">تاریخ ایجاد</p>
                  <p className="font-medium">{notification.created_at_jalali}</p>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-500">آخرین به‌روزرسانی</p>
                  <p className="font-medium">{notification.updated_at_jalali}</p>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-3">
                {notification.link && (
                  <a
                    href={notification.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <i className="fas fa-external-link-alt"></i>
                    باز کردن لینک
                  </a>
                )}
                
                {!notification.is_read && (
                  <button
                    onClick={markAsRead}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <i className="fas fa-check"></i>
                    علامت خوانده‌شده
                  </button>
                )}
                
                {!notification.is_archived && (
                  <button
                    onClick={archiveNotification}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <i className="fas fa-archive"></i>
                    آرشیو کردن
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default DetailNotification; 