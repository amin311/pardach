import React, { useState, useEffect } from 'react';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaPlus, FaEye, FaEdit, FaTrash, FaDownload, FaCheck, FaExclamationTriangle } from 'react-icons/fa';

// کامپوننت کارت قالب کاربر
const UserTemplateCard = ({ userTemplate, onDelete }) => {
  const navigate = useNavigate();
  
  // تبدیل تاریخ به فرمت مناسب
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <motion.div 
      className="bg-white rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg"
      whileHover={{ y: -5 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {userTemplate.template?.preview_image && (
        <div className="h-48 overflow-hidden bg-gray-100">
          <img 
            src={userTemplate.template.preview_image} 
            alt={userTemplate.name || userTemplate.template.title} 
            className="w-full h-full object-cover"
          />
        </div>
      )}
      
      <div className="p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">
            {userTemplate.name || userTemplate.template.title}
          </h3>
          
          <div className="flex items-center">
            {userTemplate.is_completed ? (
              <span className="flex items-center text-green-600 text-sm">
                <FaCheck className="ml-1" /> تکمیل شده
              </span>
            ) : (
              <span className="flex items-center text-yellow-500 text-sm">
                <FaExclamationTriangle className="ml-1" /> ناتمام
              </span>
            )}
          </div>
        </div>
        
        <p className="text-gray-500 text-sm mb-3 truncate">
          {userTemplate.description || userTemplate.template.description || 'بدون توضیحات'}
        </p>
        
        <div className="border-t pt-3">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm text-gray-500">
              تاریخ ایجاد: {formatDate(userTemplate.created_at)}
            </span>
            <span className="font-bold text-blue-600">
              {userTemplate.final_price.toLocaleString()} تومان
            </span>
          </div>
          
          <div className="flex justify-between">
            <div className="flex space-x-2 space-x-reverse">
              <button
                onClick={() => navigate(`/user-templates/${userTemplate.id}`)}
                className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                title="مشاهده جزئیات"
              >
                <FaEye />
              </button>
              
              <button
                onClick={() => navigate(`/user-templates/${userTemplate.id}/edit`)}
                className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100"
                title="ویرایش"
              >
                <FaEdit />
              </button>
              
              <button
                onClick={() => onDelete(userTemplate.id)}
                className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
                title="حذف"
              >
                <FaTrash />
              </button>
            </div>
            
            {userTemplate.is_completed && (
              <button
                className="flex items-center px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700"
                title="دانلود"
              >
                <FaDownload className="ml-1" /> دانلود
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// کامپوننت صفحه لیست قالب‌های کاربر
const UserTemplates = () => {
  const navigate = useNavigate();
  const [userTemplates, setUserTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // بارگذاری قالب‌های کاربر
  useEffect(() => {
    fetchUserTemplates();
  }, []);
  
  const fetchUserTemplates = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/templates/user-templates/');
      setUserTemplates(response.data);
      setError(null);
    } catch (err) {
      setError('خطا در بارگذاری قالب‌های کاربر');
      toast.error('خطا در بارگذاری لیست قالب‌های کاربر');
      console.error('Error fetching user templates:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // حذف قالب کاربر
  const handleDelete = async (userTemplateId) => {
    if (!window.confirm('آیا از حذف این قالب اطمینان دارید؟')) {
      return;
    }
    
    try {
      await axiosInstance.delete(`/api/templates/user-templates/${userTemplateId}/`);
      toast.success('قالب با موفقیت حذف شد');
      setUserTemplates(userTemplates.filter(ut => ut.id !== userTemplateId));
    } catch (err) {
      toast.error('خطا در حذف قالب');
      console.error('Error deleting user template:', err);
    }
  };
  
  // نمایش لودینگ
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  // نمایش خطا
  if (error) {
    return (
      <div className="bg-red-100 text-red-700 p-4 rounded-lg my-4">
        <h2 className="text-lg font-bold mb-2">خطا</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">قالب‌های من</h1>
        
        <Link 
          to="/templates" 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <FaPlus className="ml-2" /> استفاده از قالب جدید
        </Link>
      </div>
      
      {userTemplates.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h2 className="text-xl text-gray-700 mb-4">هنوز هیچ قالبی ایجاد نکرده‌اید!</h2>
          <p className="text-gray-500 mb-6">برای ایجاد یک قالب جدید، ابتدا یک قالب را از لیست قالب‌ها انتخاب کنید.</p>
          <Link 
            to="/templates" 
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <FaPlus className="ml-2" /> مشاهده قالب‌ها
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {userTemplates.map(userTemplate => (
            <UserTemplateCard 
              key={userTemplate.id} 
              userTemplate={userTemplate} 
              onDelete={handleDelete} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default UserTemplates; 