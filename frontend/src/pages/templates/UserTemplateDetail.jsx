import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowRight, FaEdit, FaTrash, FaDownload, FaUser, FaCalendarAlt, FaMoneyBillWave, FaClipboardCheck } from 'react-icons/fa';

// کامپوننت نمایش بخش کاربر
const UserSectionCard = ({ section, userSection }) => {
  const [expanded, setExpanded] = useState(false);

  // تبدیل تاریخ به فرمت مناسب
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mb-4">
      <div 
        className="p-4 cursor-pointer flex justify-between items-center hover:bg-gray-50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center">
          <h3 className="text-lg font-semibold text-gray-800">
            {userSection.section.name || `بخش ${userSection.section.order}`}
          </h3>
          {userSection.is_completed && (
            <span className="mr-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
              تکمیل شده
            </span>
          )}
        </div>
        <span className="transform transition-transform duration-200" style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0)' }}>
          &#10095;
        </span>
      </div>
      
      {expanded && (
        <div className="px-4 pb-4 border-t">
          {userSection.section.description && (
            <p className="text-gray-600 mb-4 mt-2">
              {userSection.section.description}
            </p>
          )}
          
          {/* نمایش ورودی‌های طراحی کاربر */}
          {userSection.user_design_inputs && userSection.user_design_inputs.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-700 mb-2">ورودی‌های طراحی:</h4>
              <div className="space-y-3">
                {userSection.user_design_inputs.map(input => (
                  <div key={input.id} className="border rounded-md p-3 bg-gray-50">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">{input.design_input.name || `ورودی ${input.order}`}</span>
                      {input.design && (
                        <span className="text-sm text-blue-600">طرح انتخابی: {input.design.title}</span>
                      )}
                    </div>
                    {input.design_input.description && (
                      <p className="text-sm text-gray-500">{input.design_input.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* نمایش شرایط انتخاب شده کاربر */}
          {userSection.user_conditions && userSection.user_conditions.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700 mb-2">شرایط انتخاب شده:</h4>
              <div className="space-y-3">
                {userSection.user_conditions.map(condition => (
                  <div key={condition.id} className="border rounded-md p-3 bg-gray-50">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">{condition.condition.name}</span>
                      <span className="text-sm">
                        {condition.condition.condition_type === 'checkbox' ? 
                          (condition.value === 'true' ? 'انتخاب شده' : 'انتخاب نشده') : 
                          `مقدار: ${condition.value || 'تعیین نشده'}`
                        }
                      </span>
                    </div>
                    {condition.condition.description && (
                      <p className="text-sm text-gray-500">{condition.condition.description}</p>
                    )}
                    {condition.condition.affects_pricing && condition.value === 'true' && (
                      <div className="mt-1 text-sm text-green-600">
                        تأثیر در قیمت: {Number(condition.condition.price_factor).toLocaleString()} تومان
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// کامپوننت اصلی صفحه جزئیات قالب کاربر
const UserTemplateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [userTemplate, setUserTemplate] = useState(null);
  const [userSections, setUserSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // بارگذاری اطلاعات قالب کاربر و بخش‌های آن
  useEffect(() => {
    fetchUserTemplateDetails();
  }, [id]);
  
  const fetchUserTemplateDetails = async () => {
    try {
      setLoading(true);
      // دریافت اطلاعات قالب کاربر
      const templateResponse = await axiosInstance.get(`/api/templates/user-templates/${id}/`);
      setUserTemplate(templateResponse.data);
      
      // دریافت بخش‌های قالب کاربر
      const sectionsResponse = await axiosInstance.get(`/api/templates/user-templates/${id}/sections/`);
      setUserSections(sectionsResponse.data);
      
      setError(null);
    } catch (err) {
      setError('خطا در بارگذاری اطلاعات قالب کاربر');
      toast.error('خطا در بارگذاری اطلاعات قالب کاربر');
      console.error('Error fetching user template details:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // حذف قالب کاربر
  const handleDelete = async () => {
    if (!window.confirm('آیا از حذف این قالب اطمینان دارید؟')) {
      return;
    }
    
    try {
      await axiosInstance.delete(`/api/templates/user-templates/${id}/`);
      toast.success('قالب با موفقیت حذف شد');
      navigate('/user-templates');
    } catch (err) {
      toast.error('خطا در حذف قالب');
      console.error('Error deleting user template:', err);
    }
  };
  
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
  
  // نمایش لودینگ
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  // نمایش خطا
  if (error || !userTemplate) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 text-red-700 p-4 rounded-lg my-4">
          <h2 className="text-lg font-bold mb-2">خطا</h2>
          <p>{error || 'قالب کاربر یافت نشد'}</p>
          <button
            onClick={() => navigate('/user-templates')}
            className="mt-4 bg-white px-4 py-2 rounded-md shadow-sm hover:bg-gray-50"
          >
            بازگشت به لیست قالب‌ها
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <button
          onClick={() => navigate('/user-templates')}
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <FaArrowRight className="ml-1" /> بازگشت به لیست قالب‌های من
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
        <div className="md:flex">
          {userTemplate.template?.preview_image && (
            <div className="md:w-1/3 h-64 overflow-hidden">
              <img 
                src={userTemplate.template.preview_image} 
                alt={userTemplate.name || userTemplate.template.title} 
                className="w-full h-full object-cover"
              />
            </div>
          )}
          
          <div className="p-6 md:w-2/3">
            <div className="flex justify-between items-start">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">
                {userTemplate.name || userTemplate.template.title}
              </h1>
              
              <div className="flex space-x-2 space-x-reverse">
                <button
                  onClick={() => navigate(`/user-templates/${userTemplate.id}/edit`)}
                  className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100"
                  title="ویرایش"
                >
                  <FaEdit />
                </button>
                
                <button
                  onClick={handleDelete}
                  className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
                  title="حذف"
                >
                  <FaTrash />
                </button>
              </div>
            </div>
            
            <p className="text-gray-600 mb-4">
              {userTemplate.description || userTemplate.template.description || 'بدون توضیحات'}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="flex items-center text-gray-600">
                <FaCalendarAlt className="ml-2 text-blue-500" /> 
                <span>تاریخ ایجاد: {formatDate(userTemplate.created_at)}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <FaUser className="ml-2 text-blue-500" /> 
                <span>قالب اصلی: {userTemplate.template.title}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <FaMoneyBillWave className="ml-2 text-blue-500" /> 
                <span>قیمت نهایی: {userTemplate.final_price.toLocaleString()} تومان</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <FaClipboardCheck className="ml-2 text-blue-500" /> 
                <span>وضعیت: {userTemplate.is_completed ? 'تکمیل شده' : 'ناتمام'}</span>
              </div>
            </div>
            
            {userTemplate.is_completed && (
              <div className="mt-4">
                <button
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <FaDownload className="ml-2" /> دانلود طرح نهایی
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xl font-bold text-gray-800 mb-4">بخش‌های قالب</h2>
        
        {userSections.length === 0 ? (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 text-center">
            <p className="text-gray-600">هیچ بخشی برای این قالب تعریف نشده است.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {userSections.map(userSection => (
              <UserSectionCard 
                key={userSection.id} 
                userSection={userSection}
              />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default UserTemplateDetail; 