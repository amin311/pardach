import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';

const UserForm = ({ isAdmin, isEdit = false }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
    current_role: ''
  });

  // بارگذاری اطلاعات کاربر در حالت ویرایش
  useEffect(() => {
    if (isAdmin) {
      // دریافت نقش‌ها
      fetchRoles();
      
      // دریافت اطلاعات کاربر در حالت ویرایش
      if (isEdit && id) {
        fetchUser(id);
      }
    }
  }, [isAdmin, isEdit, id]);

  // دریافت لیست نقش‌ها
  const fetchRoles = async () => {
    try {
      const response = await axios.get('/api/auth/roles/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setRoles(response.data);
    } catch (error) {
      toast.error('خطا در دریافت نقش‌ها');
      console.error(error);
    }
  };

  // دریافت اطلاعات کاربر برای ویرایش
  const fetchUser = async (userId) => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/auth/users/${userId}/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      // بروزرسانی state با اطلاعات کاربر
      setFormData({
        username: response.data.username,
        email: response.data.email,
        password: '', // رمز عبور نمایش داده نمی‌شود
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        is_active: response.data.is_active,
        is_staff: response.data.is_staff,
        current_role: response.data.current_role || ''
      });
    } catch (error) {
      toast.error('خطا در دریافت اطلاعات کاربر');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // تغییر مقادیر فرم
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // ارسال فرم
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const payload = { ...formData };
      
      // در حالت ویرایش اگر رمز عبور وارد نشده باشد، از ارسال آن صرف نظر می‌کنیم
      if (isEdit && !payload.password) {
        delete payload.password;
      }
      
      if (isEdit) {
        // ویرایش کاربر
        await axios.put(`/api/auth/users/${id}/`, payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        toast.success('کاربر با موفقیت ویرایش شد');
      } else {
        // ایجاد کاربر جدید
        await axios.post('/api/auth/users/', payload, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        toast.success('کاربر با موفقیت ایجاد شد');
      }
      
      // هدایت به صفحه لیست کاربران
      navigate('/users');
    } catch (error) {
      toast.error(isEdit ? 'خطا در ویرایش کاربر' : 'خطا در ایجاد کاربر');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  // بررسی دسترسی ادمین
  if (!isAdmin) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div className="text-center p-6 bg-gray-100 rounded-lg shadow">
          <div className="text-5xl text-red-500 mb-4">🔒</div>
          <h2 className="text-xl font-bold mb-2">دسترسی محدود</h2>
          <p className="text-gray-600">فقط ادمین‌ها به این صفحه دسترسی دارند.</p>
        </div>
      </div>
    );
  }

  // نمایش لودینگ
  if (loading && isEdit) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-xl">
      <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
        <span className="text-3xl">{isEdit ? '✏️' : '➕'}</span>
        {isEdit ? 'ویرایش کاربر' : 'افزودن کاربر جدید'}
      </h1>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white p-6 rounded-lg shadow-md"
      >
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
              نام کاربری *
            </label>
            <input
              type="text"
              id="username"
              name="username"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={isEdit} // در حالت ویرایش نام کاربری قابل تغییر نیست
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              ایمیل *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              {isEdit ? 'رمز عبور (در صورت تغییر)' : 'رمز عبور *'}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              value={formData.password}
              onChange={handleChange}
              required={!isEdit} // در حالت ایجاد کاربر الزامی است
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="first_name">
                نام
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                value={formData.first_name}
                onChange={handleChange}
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="last_name">
                نام خانوادگی
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                value={formData.last_name}
                onChange={handleChange}
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="current_role">
              نقش کاربر
            </label>
            <select
              id="current_role"
              name="current_role"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              value={formData.current_role}
              onChange={handleChange}
            >
              <option value="">بدون نقش</option>
              {roles.map(role => (
                <option key={role.name} value={role.name}>
                  {role.name} - {role.description}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4 flex items-center">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              className="w-5 h-5 text-blue-600"
              checked={formData.is_active}
              onChange={handleChange}
            />
            <label className="mr-2 text-gray-700" htmlFor="is_active">
              کاربر فعال است
            </label>
          </div>
          
          <div className="mb-6 flex items-center">
            <input
              type="checkbox"
              id="is_staff"
              name="is_staff"
              className="w-5 h-5 text-blue-600"
              checked={formData.is_staff}
              onChange={handleChange}
            />
            <label className="mr-2 text-gray-700" htmlFor="is_staff">
              دسترسی ادمین
            </label>
          </div>
          
          <div className="flex gap-3">
            <button
              type="submit"
              className={`flex-1 py-2 px-4 rounded text-white font-bold ${loading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'} transition duration-200 flex items-center justify-center gap-2`}
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  در حال پردازش...
                </>
              ) : (
                <>
                  <span>{isEdit ? '✓' : '+'}</span>
                  {isEdit ? 'ذخیره تغییرات' : 'ایجاد کاربر'}
                </>
              )}
            </button>
            
            <Link
              to="/users"
              className="flex-1 py-2 px-4 bg-gray-300 text-gray-800 rounded font-bold hover:bg-gray-400 transition duration-200 text-center"
            >
              انصراف
            </Link>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default UserForm; 