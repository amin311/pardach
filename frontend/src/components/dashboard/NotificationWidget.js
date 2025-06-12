import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';

const NotificationWidget = () => {
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNotifications = async () => {
      setLoading(true);
      try {
        const response = await axiosInstance.get('/api/notifications/?unread=true&limit=5');
        setNotifications(response.data.results || []);
        setError(null);
      } catch (err) {
        setError('خطا در بارگذاری اعلان‌ها');
        toast.error('خطا در بارگذاری اعلان‌ها');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id) => {
    try {
      await axiosInstance.patch(`/api/notifications/${id}/`, { read: true });
      setNotifications(notifications.filter(notification => notification.id !== id));
      toast.success('اعلان خوانده شد');
    } catch (err) {
      toast.error('خطا در به‌روزرسانی وضعیت اعلان');
      console.error(err);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'order':
        return <i className="fas fa-shopping-cart text-blue-500"></i>;
      case 'payment':
        return <i className="fas fa-credit-card text-green-500"></i>;
      case 'system':
        return <i className="fas fa-cog text-gray-500"></i>;
      case 'message':
        return <i className="fas fa-envelope text-purple-500"></i>;
      default:
        return <i className="fas fa-bell text-yellow-500"></i>;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full flex justify-center items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-gray-600">در حال بارگذاری اعلان‌ها...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full flex justify-center items-center">
        <div className="text-center text-red-500">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-lg shadow-md p-4 h-full"
    >
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
        <i className="fas fa-bell text-yellow-500 ml-2"></i> اعلان‌های اخیر
      </h3>
      
      {notifications.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <i className="fas fa-check-circle text-green-500 text-3xl mb-2"></i>
          <p>شما هیچ اعلان نخوانده‌ای ندارید</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map(notification => (
            <motion.div 
              key={notification.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="p-3 rounded-lg bg-gray-50 border-r-4 border-blue-500 flex items-start"
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center ml-3 flex-shrink-0">
                {getNotificationIcon(notification.type)}
              </div>
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900">{notification.title}</h4>
                <p className="text-sm text-gray-600">{notification.message}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">{notification.created_at_jalali}</span>
                  <div className="flex space-x-2 space-x-reverse">
                    {notification.link && (
                      <Link to={notification.link} className="text-xs text-blue-500 hover:underline">
                        مشاهده
                      </Link>
                    )}
                    <button 
                      onClick={() => handleMarkAsRead(notification.id)}
                      className="text-xs text-gray-500 hover:text-gray-700"
                    >
                      خوانده شد
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
      
      <div className="mt-4 text-center">
        <Link to="/notifications" className="text-blue-500 text-sm hover:underline">
          مشاهده همه اعلان‌ها
        </Link>
      </div>
    </motion.div>
  );
};

export default NotificationWidget; 