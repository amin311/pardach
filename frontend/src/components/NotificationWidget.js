import React, { useState, useEffect, useRef } from 'react';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';

const NotificationWidget = ({ userId }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const wsRef = useRef(null);

  // اتصال به وب‌سوکت برای دریافت اعلانات بلادرنگ
  useEffect(() => {
    if (userId) {
      // دریافت اعلانات از API
      fetchNotifications();

      // اتصال به WebSocket
      const wsUrl = `ws://${window.location.host}/ws/notifications/${userId}/`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('اتصال به سرویس اعلانات برقرار شد');
      };

      wsRef.current.onmessage = (e) => {
        const data = JSON.parse(e.data);
        
        if (data.type === 'new_notification') {
          // افزودن اعلان جدید به لیست
          handleNewNotification(data.notification);
        } else if (data.type === 'unread_notifications') {
          // دریافت اعلانات خوانده نشده هنگام اتصال
          setNotifications(prevNotifications => {
            const newNotifications = [...data.notifications, ...prevNotifications];
            // حذف تکراری‌ها
            return [...new Map(newNotifications.map(item => [item.id, item])).values()];
          });
          setUnreadCount(data.notifications.length);
        }
      };

      wsRef.current.onerror = (e) => {
        console.error('خطا در اتصال به سرویس اعلانات:', e);
      };

      wsRef.current.onclose = () => {
        console.log('اتصال به سرویس اعلانات بسته شد');
      };

      // بستن اتصال هنگام از بین رفتن کامپوننت
      return () => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [userId]);

  // بستن دراپ‌داون با کلیک خارج از آن
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // دریافت اعلانات از API
  const fetchNotifications = async () => {
    try {
      setIsLoading(true);
      const response = await axiosInstance.get('/api/notification/?is_read=false&is_archived=false', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setNotifications(response.data);
      setUnreadCount(response.data.length);
      setIsLoading(false);
    } catch (error) {
      console.error('خطا در دریافت اعلانات:', error);
      setIsLoading(false);
      toast.error('خطا در بارگذاری اعلانات');
    }
  };

  // افزودن اعلان جدید به لیست
  const handleNewNotification = (notification) => {
    setNotifications(prevNotifications => [notification, ...prevNotifications]);
    setUnreadCount(prevCount => prevCount + 1);
    
    // نمایش toast برای اعلان جدید
    toast.info(
      <div>
        <strong>{notification.title}</strong>
        <p>{notification.content.substring(0, 50)}...</p>
      </div>,
      {
        onClick: () => {
          if (notification.link) {
            window.location.href = notification.link;
          }
        }
      }
    );
  };

  // علامت‌گذاری اعلان به عنوان خوانده‌شده
  const markAsRead = async (notificationId) => {
    try {
      await axiosInstance.post(`/api/notification/${notificationId}/read/`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      // به‌روزرسانی وضعیت اعلان در لیست
      setNotifications(prevNotifications => 
        prevNotifications.filter(notification => notification.id !== notificationId)
      );
      setUnreadCount(prevCount => prevCount - 1);
    } catch (error) {
      console.error('خطا در علامت‌گذاری اعلان:', error);
      toast.error('خطا در علامت‌گذاری اعلان');
    }
  };

  // علامت‌گذاری همه اعلانات به عنوان خوانده‌شده
  const markAllAsRead = async () => {
    try {
      await axiosInstance.post('/api/notification/mark-all-read/', {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setNotifications([]);
      setUnreadCount(0);
      toast.success('تمام اعلانات خوانده شدند');
    } catch (error) {
      console.error('خطا در علامت‌گذاری اعلانات:', error);
      toast.error('خطا در علامت‌گذاری اعلانات');
    }
  };

  // آیکون مناسب برای هر نوع اعلان
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'order_status':
        return <i className="fas fa-shopping-cart text-blue-500"></i>;
      case 'payment_status':
        return <i className="fas fa-money-bill-wave text-green-500"></i>;
      case 'business_activity':
        return <i className="fas fa-briefcase text-purple-500"></i>;
      case 'system':
        return <i className="fas fa-cog text-red-500"></i>;
      case 'user':
        return <i className="fas fa-user text-orange-500"></i>;
      default:
        return <i className="fas fa-bell text-gray-500"></i>;
    }
  };

  // تنظیمات اسلایدر
  const sliderSettings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: notifications.length < 3 ? notifications.length : 3,
    slidesToScroll: 1,
    rtl: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: notifications.length < 2 ? notifications.length : 2,
          slidesToScroll: 1,
        }
      },
      {
        breakpoint: 640,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
  };

  if (isLoading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md animate-pulse">
        <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
        <div className="h-24 bg-gray-200 rounded"></div>
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
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <i className="fas fa-bell text-blue-500"></i> اعلانات اخیر
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
              {unreadCount}
            </span>
          )}
        </h3>
        
        <div className="relative" ref={dropdownRef}>
          <button 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="p-2 text-gray-500 hover:text-blue-500 transition-colors"
          >
            <i className="fas fa-ellipsis-v"></i>
          </button>
          
          <AnimatePresence>
            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white z-10"
              >
                <div className="py-1">
                  <button
                    onClick={markAllAsRead}
                    className="w-full text-right px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fas fa-check-double mr-2"></i>
                    علامت‌گذاری همه به عنوان خوانده‌شده
                  </button>
                  <Link
                    to="/notifications"
                    className="block text-right px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <i className="fas fa-list mr-2"></i>
                    مشاهده همه اعلانات
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {notifications.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          <i className="fas fa-bell-slash text-gray-400 text-3xl mb-2"></i>
          <p>اعلانی وجود ندارد</p>
        </div>
      ) : (
        <Slider {...sliderSettings}>
          {notifications.map(notification => (
            <div key={notification.id} className="px-2">
              <motion.div 
                whileHover={{ scale: 1.03 }}
                className="border rounded-lg p-3 h-36 flex flex-col relative"
              >
                <div className="flex items-start gap-2">
                  <div className="p-2 rounded-full bg-gray-100">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <h4 className="font-bold text-sm mb-1 truncate">{notification.title}</h4>
                    <p className="text-xs text-gray-600 line-clamp-2 mb-2">{notification.content}</p>
                    <p className="text-xs text-gray-500">{notification.created_at_jalali}</p>
                  </div>
                </div>
                
                <div className="mt-auto pt-2 flex items-center justify-between">
                  {notification.link ? (
                    <Link 
                      to={notification.link}
                      className="text-blue-500 text-xs hover:underline"
                      onClick={() => markAsRead(notification.id)}
                    >
                      مشاهده جزئیات
                    </Link>
                  ) : (
                    <span></span>
                  )}
                  <button
                    onClick={() => markAsRead(notification.id)}
                    className="text-gray-500 text-xs hover:text-blue-500"
                  >
                    <i className="fas fa-check mr-1"></i>
                    خوانده شد
                  </button>
                </div>
              </motion.div>
            </div>
          ))}
        </Slider>
      )}
      
      <div className="mt-3 text-center">
        <Link to="/notifications" className="text-blue-500 text-sm hover:underline">
          مشاهده همه اعلانات
        </Link>
      </div>
    </motion.div>
  );
};

export default NotificationWidget; 