import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import NotificationWidget from './NotificationWidget';

const Navbar = ({ user, isAdmin, setUser }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
  };
  
  const isActive = (path) => {
    return location.pathname === path ? 'bg-blue-700' : '';
  };
  
  const isActiveGroup = (paths) => {
    return paths.some(path => location.pathname.startsWith(path)) ? 'bg-gray-700' : '';
  };
  
  // اضافه کردن لینک قالب‌ها به منوی ناوبری
  const navItems = [
    { title: 'صفحه اصلی', path: '/' },
    { title: 'طرح‌ها', path: '/designs' },
    { title: 'قالب‌ها', path: '/templates' },
    { title: 'قالب‌های من', path: '/user-templates' },
    { title: 'سفارش‌ها', path: '/orders' },
    // سایر آیتم‌های منو
  ];
  
  if (!user) return null;
  
  return (
    <nav className="bg-gray-800 text-white">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* لوگو و منوی اصلی */}
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold">سیستم مدیریت طرح‌ها</Link>
            
            {/* منوی دسکتاپ */}
            <div className="hidden md:flex md:mr-10 space-x-4 space-x-reverse">
              <Link 
                to="/" 
                className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
              >
                داشبورد
              </Link>
              
              <div className="relative group">
                <button 
                  className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/designs'])}`}
                >
                  طرح‌ها
                </button>
                <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link 
                    to="/designs" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    لیست طرح‌ها
                  </Link>
                  <Link 
                    to="/designs/create" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    ایجاد طرح جدید
                  </Link>
                  <Link 
                    to="/designs/batch-upload" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    آپلود دسته‌ای
                  </Link>
                </div>
              </div>
              
              <div className="relative group">
                <button 
                  className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/templates', '/user-templates'])}`}
                >
                  قالب‌ها
                </button>
                <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link 
                    to="/templates" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    لیست قالب‌ها
                  </Link>
                  <Link 
                    to="/user-templates" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    قالب‌های من
                  </Link>
                </div>
              </div>
              
              <div className="relative group">
                <button 
                  className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/orders'])}`}
                >
                  سفارش‌ها
                </button>
                <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link 
                    to="/orders" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    لیست سفارش‌ها
                  </Link>
                  <Link 
                    to="/orders/create" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    ایجاد سفارش جدید
                  </Link>
                </div>
              </div>
              
              <div className="relative group">
                <button 
                  className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/chats', '/notifications'])}`}
                >
                  ارتباطات
                </button>
                <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link 
                    to="/chats" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    گفتگوها
                  </Link>
                  <Link 
                    to="/chats/create" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    گفتگوی جدید
                  </Link>
                  <Link 
                    to="/notifications" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    اعلان‌ها
                  </Link>
                </div>
              </div>
              
              <div className="relative group">
                <button 
                  className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/reports'])}`}
                >
                  گزارش‌ها
                </button>
                <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link 
                    to="/reports" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    لیست گزارش‌ها
                  </Link>
                  <Link 
                    to="/reports/generate" 
                    className="block px-4 py-2 text-sm hover:bg-gray-100"
                  >
                    تولید گزارش جدید
                  </Link>
                </div>
              </div>
              
              {isAdmin && (
                <>
                  <div className="relative group">
                    <button 
                      className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none ${isActiveGroup(['/users'])}`}
                    >
                      کاربران
                    </button>
                    <div className="absolute z-10 right-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg py-1 hidden group-hover:block">
                      <Link 
                        to="/users" 
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        لیست کاربران
                      </Link>
                      <Link 
                        to="/users/create" 
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        ایجاد کاربر
                      </Link>
                    </div>
                  </div>
                  
                  <Link 
                    to="/settings" 
                    className={`px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 ${isActive('/settings')}`}
                  >
                    تنظیمات
                  </Link>
                </>
              )}
            </div>
          </div>
          
          {/* پروفایل کاربر */}
          <div className="flex items-center">
            {user ? (
              <>
                <div className="mr-4">
                  <NotificationWidget userId={user?.id} />
                </div>
                <div className="hidden md:block mr-4">
                  <div className="flex items-center">
                    <div className="text-sm">
                      <span className="text-white">{user.username}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="mr-4 px-3 py-2 rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                    >
                      خروج
                    </button>
                  </div>
                </div>
              </>
            ) : (
              // ... existing code ...
            )}
            
            {/* دکمه همبرگر برای موبایل */}
            <div className="md:hidden">
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:bg-gray-700 focus:text-white"
              >
                <svg
                  className="h-6 w-6"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  {isOpen ? (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  ) : (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* منوی موبایل */}
      <motion.div
        className={`md:hidden ${isOpen ? 'block' : 'hidden'}`}
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: isOpen ? 1 : 0, height: isOpen ? 'auto' : 0 }}
        transition={{ duration: 0.2 }}
      >
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <Link
            to="/"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            داشبورد
          </Link>
          
          <Link
            to="/designs"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/designs')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            لیست طرح‌ها
          </Link>
          
          <Link
            to="/designs/create"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/designs/create')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            ایجاد طرح جدید
          </Link>
          
          <Link
            to="/designs/batch-upload"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/designs/batch-upload')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            آپلود دسته‌ای
          </Link>
          
          <Link
            to="/templates"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/templates')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            لیست قالب‌ها
          </Link>
          
          <Link
            to="/user-templates"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/user-templates')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            قالب‌های من
          </Link>
          
          <Link
            to="/orders"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/orders')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            لیست سفارش‌ها
          </Link>
          
          <Link
            to="/orders/create"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/orders/create')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            ایجاد سفارش جدید
          </Link>
          
          <Link
            to="/chats"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/chats')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            گفتگوها
          </Link>
          
          <Link
            to="/notifications"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/notifications')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            اعلان‌ها
          </Link>
          
          <Link
            to="/reports"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/reports')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            گزارش‌ها
          </Link>
          
          <Link
            to="/reports/generate"
            className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/reports/generate')} hover:bg-gray-700`}
            onClick={() => setIsOpen(false)}
          >
            تولید گزارش جدید
          </Link>
          
          {isAdmin && (
            <>
              <Link
                to="/users"
                className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/users')} hover:bg-gray-700`}
                onClick={() => setIsOpen(false)}
              >
                لیست کاربران
              </Link>
              
              <Link
                to="/users/create"
                className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/users/create')} hover:bg-gray-700`}
                onClick={() => setIsOpen(false)}
              >
                ایجاد کاربر
              </Link>
              
              <Link
                to="/settings"
                className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/settings')} hover:bg-gray-700`}
                onClick={() => setIsOpen(false)}
              >
                تنظیمات
              </Link>
            </>
          )}
          
          <div className="border-t border-gray-700 pt-3 pb-2">
            <div className="flex items-center justify-between px-3">
              <div className="text-base font-medium">{user.username}</div>
              <button
                onClick={handleLogout}
                className="px-3 py-2 rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                خروج
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </nav>
  );
};

export default Navbar; 