import React, { useState } from 'react';
<<<<<<< HEAD
import axiosInstance from '../lib/axios';
=======
import axiosInstance from '../api/axiosInstance';
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

const AuthWidget = ({ setUser }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      let response;
      
      if (isLogin) {
        // ورود کاربر
        response = await axiosInstance.post('/api/auth/login/', {
          username: formData.username,
          password: formData.password
        });
        toast.success('ورود موفق');
      } else {
        // ثبت‌نام کاربر جدید
        response = await axiosInstance.post('/api/auth/register/', formData);
        toast.success('ثبت‌نام موفق');
      }
      
      // ذخیره توکن‌ها در localStorage
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      // به‌روزرسانی وضعیت کاربر در کامپوننت والد
      setUser(response.data.user);
      
      // هدایت به صفحه اصلی (می‌تواند با react-router-dom انجام شود)
      window.location.href = '/';
      
    } catch (error) {
      toast.error(isLogin ? 'خطا در ورود' : 'خطا در ثبت‌نام');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md"
      >
        <h2 className="text-2xl font-bold text-center mb-6 flex items-center justify-center">
          <span className="ml-2 text-3xl">
            {isLogin ? '🔑' : '✨'}
          </span>
          {isLogin ? 'ورود به حساب کاربری' : 'ثبت‌نام در سیستم'}
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
              نام کاربری
            </label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          
          {!isLogin && (
            <>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                  ایمیل
                </label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="first_name">
                  نام
                </label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="last_name">
                  نام خانوادگی
                </label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
            </>
          )}
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              رمز عبور
            </label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <button
            className={`w-full py-2 px-4 rounded font-bold text-white ${loading ? 'bg-gray-400' : isLogin ? 'bg-blue-500 hover:bg-blue-600' : 'bg-green-500 hover:bg-green-600'} transition duration-200`}
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                در حال پردازش...
              </span>
            ) : (
              <span className="flex items-center justify-center">
                <span className="ml-2">{isLogin ? '🔐' : '📝'}</span>
                {isLogin ? 'ورود' : 'ثبت‌نام'}
              </span>
            )}
          </button>
        </form>
        
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {isLogin ? 'حساب کاربری ندارید؟' : 'قبلاً ثبت‌نام کرده‌اید؟'}
            <button
              onClick={toggleMode}
              className="text-blue-500 hover:text-blue-700 mr-1 focus:outline-none"
            >
              {isLogin ? 'ثبت‌نام کنید' : 'وارد شوید'}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default AuthWidget; 