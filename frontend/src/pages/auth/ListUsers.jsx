import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ListUsers = ({ userId, isAdmin }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // بارگذاری لیست کاربران در لود اولیه صفحه
  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [isAdmin]);

  // دریافت لیست کاربران از سرور
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/auth/users/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setUsers(response.data);
    } catch (error) {
      toast.error('خطا در بارگذاری کاربران');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // حذف کاربر با تأیید قبلی
  const handleDelete = async (userId) => {
    if (window.confirm('آیا از حذف کاربر مطمئن هستید؟')) {
      try {
        await axios.delete(`/api/auth/users/${userId}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setUsers(users.filter(user => user.id !== userId));
        toast.success('کاربر با موفقیت حذف شد');
      } catch (error) {
        toast.error('خطا در حذف کاربر');
        console.error(error);
      }
    }
  };

  // تبدیل تاریخ به شمسی (در اصل باید از کتابخانه یا API سرور استفاده کرد)
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
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
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
        <span className="text-3xl">👥</span>
        مدیریت کاربران
      </h1>
      
      <div className="mb-6 flex flex-wrap gap-4 justify-between items-center">
        {/* جستجو */}
        <div className="relative flex-grow max-w-xl">
          <input
            type="text"
            className="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="جستجوی کاربر..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <span className="absolute left-3 top-3 text-gray-400">🔍</span>
        </div>
        
        {/* دکمه افزودن کاربر */}
        <Link
          to="/users/create"
          className="bg-green-500 text-white py-3 px-6 rounded-lg flex items-center gap-2 hover:bg-green-600 transition duration-200"
        >
          <span>➕</span>
          افزودن کاربر جدید
        </Link>
      </div>
      
      {/* لیست کاربران */}
      {users.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-5xl mb-4">🔍</div>
          <p>هیچ کاربری یافت نشد</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {users
            .filter(user => 
              user.username.toLowerCase().includes(search.toLowerCase()) ||
              user.email.toLowerCase().includes(search.toLowerCase()) ||
              (user.first_name && user.first_name.toLowerCase().includes(search.toLowerCase())) ||
              (user.last_name && user.last_name.toLowerCase().includes(search.toLowerCase()))
            )
            .map(user => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-white rounded-lg shadow-md overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-xl">
                      {user.first_name ? user.first_name[0]?.toUpperCase() : user.username[0]?.toUpperCase()}
                    </div>
                    <div className="mr-4">
                      <h3 className="font-bold text-lg">{user.username}</h3>
                      <p className="text-sm text-gray-600">{user.email}</p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm">
                      <span className="font-semibold">نام:</span> {user.first_name} {user.last_name}
                    </p>
                    <p className="text-sm">
                      <span className="font-semibold">نقش:</span> {user.current_role || 'تعیین نشده'}
                    </p>
                    <p className="text-sm">
                      <span className="font-semibold">تاریخ ثبت‌نام:</span> {formatDate(user.created_at)}
                    </p>
                    <p className="text-sm">
                      <span className="font-semibold">وضعیت:</span> {user.is_active ? (
                        <span className="text-green-500">فعال</span>
                      ) : (
                        <span className="text-red-500">غیرفعال</span>
                      )}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <Link
                      to={`/users/${user.id}`}
                      className="flex-1 py-2 px-3 text-center text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                    >
                      مشاهده
                    </Link>
                    <Link
                      to={`/users/edit/${user.id}`}
                      className="flex-1 py-2 px-3 text-center text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition"
                    >
                      ویرایش
                    </Link>
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="flex-1 py-2 px-3 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition"
                    >
                      حذف
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
        </div>
      )}
    </div>
  );
};

export default ListUsers; 