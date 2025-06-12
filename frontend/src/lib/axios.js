<<<<<<< HEAD
import axiosInstance from './lib/axios';

// ایجاد instance اصلی axios
const axiosInstance = axiosInstance.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor برای افزودن token به درخواست‌ها
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor برای مدیریت پاسخ‌ها و خطاها
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // اگر خطای 401 دریافت شد و قبلاً تلاش نشده
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axiosInstance.post('/api/auth/token/refresh/', {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // تکرار درخواست اصلی با token جدید
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axiosInstance(originalRequest);
        }
      } catch (refreshError) {
        // اگر refresh token نیز منقضی شده، کاربر را به صفحه لاگین هدایت کن
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance; 
=======
import axios from 'axios';

export default axios;
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
