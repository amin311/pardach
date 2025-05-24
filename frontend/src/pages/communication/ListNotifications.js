import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ListNotifications = ({ userId, isAdmin }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, read, unread

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  // دریافت اعلانات با فیلتر
  const fetchNotifications = () => {
    let url = '/api/communication/notifications/';
    
    if (filter !== 'all') {
      url += `?is_read=${filter === 'read'}`;
    }

    axios.get(url, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        setNotifications(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching notifications:', err);
        toast.error('خطا در بارگذاری اعلانات');
        setLoading(false);
      });
  };

  // علامت‌گذاری اعلان به‌عنوان خوانده‌شده
  const markAsRead = (notificationId) => {
    axios.post(`/api/communication/notifications/${notificationId}/read/`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        // به‌روزرسانی لیست اعلانات
        setNotifications(notifications.map(notification => 
          notification.id === notificationId 
            ? { ...notification, is_read: true } 
            : notification
        ));
        toast.success('اعلان به‌عنوان خوانده‌شده علامت‌گذاری شد');
      })
      .catch(err => {
        console.error('Error marking notification as read:', err);
        toast.error('خطا در علامت‌گذاری اعلان');
      });
  };

  // علامت‌گذاری همه اعلانات به‌عنوان خوانده‌شده
  const markAllAsRead = () => {
    // فیلتر کردن اعلانات خوانده نشده
    const unreadNotifications = notifications.filter(notification => !notification.is_read);
    
    if (unreadNotifications.length === 0) {
      toast.info('همه اعلانات قبلاً خوانده شده‌اند');
      return;
    }

    // علامت‌گذاری هر اعلان به‌صورت جداگانه
    Promise.all(
      unreadNotifications.map(notification => 
        axios.post(`/api/communication/notifications/${notification.id}/read/`, {}, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        })
      )
    )
      .then(() => {
        // به‌روزرسانی لیست اعلانات
        setNotifications(notifications.map(notification => ({ ...notification, is_read: true })));
        toast.success('همه اعلانات به‌عنوان خوانده‌شده علامت‌گذاری شدند');
      })
      .catch(err => {
        console.error('Error marking all notifications as read:', err);
        toast.error('خطا در علامت‌گذاری اعلانات');
      });
  };

  // آیکون مناسب بر اساس نوع اعلان
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'order_status':
        return <i className="fas fa-shopping-cart text-blue-500 text-xl"></i>;
      case 'payment_status':
        return <i className="fas fa-money-bill-wave text-green-500 text-xl"></i>;
      case 'business_activity':
        return <i className="fas fa-briefcase text-purple-500 text-xl"></i>;
      default:
        return <i className="fas fa-info-circle text-gray-500 text-xl"></i>;
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <i className="fas fa-bell"></i> اعلانات
        </h2>
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
        <i className="fas fa-bell"></i> اعلانات
      </h2>

      {/* فیلترها و اقدامات */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2">
          <label htmlFor="notification-filter" className="text-sm font-medium">فیلتر:</label>
          <select
            id="notification-filter"
            className="bg-white border rounded-md p-2 text-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">همه اعلانات</option>
            <option value="read">خوانده‌شده</option>
            <option value="unread">خوانده‌نشده</option>
          </select>
        </div>
        
        <button
          onClick={markAllAsRead}
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md flex items-center gap-2 transition-colors text-sm"
        >
          <i className="fas fa-check-double"></i>
          علامت‌گذاری همه به‌عنوان خوانده‌شده
        </button>
      </div>

      {/* لیست اعلانات */}
      {notifications.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <i className="fas fa-bell-slash text-gray-400 text-5xl mb-4"></i>
          <p className="text-gray-500">هیچ اعلانی یافت نشد</p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map((notification) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`bg-white p-4 rounded-lg shadow border-r-4 ${
                notification.is_read 
                  ? 'border-gray-300' 
                  : 'border-blue-500'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-lg">
                      {notification.title}
                      {!notification.is_read && (
                        <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-1 mr-2">
                          جدید
                        </span>
                      )}
                    </h3>
                    <span className="text-xs text-gray-500">
                      {notification.created_at_jalali}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mt-2">{notification.content}</p>
                  
                  {notification.business && (
                    <p className="text-sm text-gray-500 mt-1">
                      کسب‌وکار: {notification.business.name}
                    </p>
                  )}
                  
                  <div className="flex justify-between mt-4">
                    <div className="flex items-center gap-3">
                      {notification.link && (
                        <Link
                          to={notification.link}
                          className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1"
                        >
                          <i className="fas fa-external-link-alt"></i> مشاهده
                        </Link>
                      )}
                      {!notification.is_read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="text-green-500 hover:text-green-700 text-sm flex items-center gap-1"
                        >
                          <i className="fas fa-check"></i> علامت‌گذاری به‌عنوان خوانده‌شده
                        </button>
                      )}
                    </div>
                    
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      notification.type === 'order_status' ? 'bg-blue-100 text-blue-800' :
                      notification.type === 'payment_status' ? 'bg-green-100 text-green-800' :
                      notification.type === 'business_activity' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {notification.type === 'order_status' ? 'وضعیت سفارش' :
                       notification.type === 'payment_status' ? 'وضعیت پرداخت' :
                       notification.type === 'business_activity' ? 'فعالیت کسب‌وکار' :
                       'عمومی'}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ListNotifications; 