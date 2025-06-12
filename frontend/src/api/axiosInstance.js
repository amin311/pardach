import axios from '../lib/axios';

<<<<<<< HEAD
// تنظیمات پایه axios
=======
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

<<<<<<< HEAD
// Interceptor برای افزودن خودکار Authorization header
=======
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

<<<<<<< HEAD
// Interceptor برای مدیریت خطاهای احراز هویت
api.interceptors.response.use(
  (response) => {
    return response;
  },
=======
api.interceptors.response.use(
  (response) => response,
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await api.post('/api/auth/token/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
<<<<<<< HEAD
          
=======
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

<<<<<<< HEAD
export default api; 
=======
export default api;
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
