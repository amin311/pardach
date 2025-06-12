import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaBell, FaCheck, FaEye, FaChevronDown, FaChevronUp } from 'react-icons/fa';
import { toast } from 'react-hot-toast';

/**
 * کامپوننت نمایش اعلانات اخیر
 * @param {Array} notifications - لیست اعلانات
 */
const NotificationWidget = ({ notifications = [] }) => {
  const [expanded, setExpanded] = useState(true);
  const [selectedTab, setSelectedTab] = useState('all'); // 'all', 'unread', 'read'

  // فیلتر کردن اعلانات بر اساس تب انتخاب شده
  const filteredNotifications = notifications.filter(notification => {
    if (selectedTab === 'all') return true;
    if (selectedTab === 'unread') return !notification.read;
    if (selectedTab === 'read') return notification.read;
    return true;
  });

  // محاسبه تعداد اعلانات خوانده نشده
  const unreadCount = notifications.filter(notification => !notification.read).length;

  // انیمیشن برای اعلانات
  const containerVariants = {
    hidden: { opacity: 0, height: 0 },
    visible: { 
      opacity: 1, 
      height: 'auto',
      transition: { 
        staggerChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* هدر ویجت */}
      <div 
        className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2 text-white">
          <FaBell className="text-xl" />
          <h2 className="text-lg font-bold">اعلانات و پیام‌ها</h2>
          {unreadCount > 0 && (
            <div className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
              {unreadCount}
            </div>
          )}
        </div>
        <div className="text-white">
          {expanded ? <FaChevronUp /> : <FaChevronDown />}
        </div>
      </div>

      {/* تب‌های فیلترینگ */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex items-center gap-2 p-4 border-b">
              <button
                className={`px-3 py-1 rounded-full text-sm ${
                  selectedTab === 'all' 
                    ? 'bg-indigo-100 text-indigo-700 font-medium' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedTab('all')}
              >
                همه
              </button>
              <button
                className={`px-3 py-1 rounded-full text-sm ${
                  selectedTab === 'unread' 
                    ? 'bg-indigo-100 text-indigo-700 font-medium' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedTab('unread')}
              >
                خوانده نشده
                {unreadCount > 0 && (
                  <span className="mr-1 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>
              <button
                className={`px-3 py-1 rounded-full text-sm ${
                  selectedTab === 'read' 
                    ? 'bg-indigo-100 text-indigo-700 font-medium' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedTab('read')}
              >
                خوانده شده
              </button>
            </div>

            {/* لیست اعلانات */}
            {filteredNotifications.length > 0 ? (
              <motion.ul
                className="divide-y overflow-hidden"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
              >
                {filteredNotifications.map((notification, index) => (
                  <motion.li 
                    key={notification.id || index}
                    variants={itemVariants}
                    className={`p-4 hover:bg-gray-50 transition-colors ${
                      !notification.read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                        !notification.read ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {notification.icon || <FaBell />}
                      </div>
                      
                      <div className="flex-grow">
                        <h3 className={`font-medium ${!notification.read ? 'text-blue-700' : 'text-gray-800'}`}>
                          {notification.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message || notification.content}
                        </p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-xs text-gray-500">
                            {notification.created_at || notification.date}
                          </span>
                          <div className="flex items-center gap-2">
                            {notification.link && (
                              <Link
                                to={notification.link}
                                className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                              >
                                <FaEye size={14} />
                                <span>مشاهده</span>
                              </Link>
                            )}
                            {!notification.read && (
                              <button
                                className="text-sm text-green-600 hover:text-green-800 flex items-center gap-1"
                                onClick={() => {
                                  // اینجا می‌توان API برای خوانده شدن اعلان را فراخوانی کرد
                                  toast.info(`اعلان ${notification.id} به عنوان خوانده شده علامت‌گذاری شد`);
                                }}
                              >
                                <FaCheck size={14} />
                                <span>خوانده شده</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.li>
                ))}
              </motion.ul>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <FaBell className="mx-auto text-3xl text-gray-300 mb-2" />
                <p>اعلان جدیدی وجود ندارد</p>
              </div>
            )}

            {/* فوتر */}
            {filteredNotifications.length > 0 && (
              <div className="p-3 bg-gray-50 text-center">
                <Link 
                  to="/notifications" 
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  مشاهده همه اعلانات
                </Link>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationWidget;