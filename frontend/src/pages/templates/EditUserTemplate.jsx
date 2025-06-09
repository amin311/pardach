import React, { useState, useEffect } from 'react';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowRight, FaSave, FaTimesCircle, FaSpinner } from 'react-icons/fa';

// کامپوننت ویرایش بخش کاربر
const UserSectionEdit = ({ userSection, onUpdate }) => {
  const [expanded, setExpanded] = useState(false);
  const [completed, setCompleted] = useState(userSection.is_completed);
  const [designInputs, setDesignInputs] = useState(userSection.user_design_inputs || []);
  const [conditions, setConditions] = useState(userSection.user_conditions || []);
  const [loading, setLoading] = useState(false);

  // بروزرسانی وضعیت تکمیل بخش
  const handleCompletedChange = () => {
    setCompleted(!completed);
    onUpdate({
      id: userSection.id,
      is_completed: !completed
    });
  };

  // بروزرسانی ورودی طراحی
  const handleDesignInputChange = async (inputId, designId) => {
    try {
      setLoading(true);
      const response = await axiosInstance.put(`/api/templates/user-design-inputs/${inputId}/`, {
        design_id: designId
      });
      
      // بروزرسانی لیست ورودی‌ها
      setDesignInputs(prevInputs => 
        prevInputs.map(input => 
          input.id === inputId ? { ...input, design: response.data.design } : input
        )
      );
      
      toast.success('ورودی طراحی با موفقیت به‌روزرسانی شد');
    } catch (err) {
      toast.error('خطا در به‌روزرسانی ورودی طراحی');
      console.error('Error updating design input:', err);
    } finally {
      setLoading(false);
    }
  };

  // بروزرسانی شرط
  const handleConditionChange = async (conditionId, value) => {
    try {
      setLoading(true);
      const response = await axiosInstance.put(`/api/templates/user-conditions/${conditionId}/`, {
        value: value
      });
      
      // بروزرسانی لیست شرط‌ها
      setConditions(prevConditions => 
        prevConditions.map(condition => 
          condition.id === conditionId ? { ...condition, value: value } : condition
        )
      );
      
      toast.success('شرط با موفقیت به‌روزرسانی شد');
    } catch (err) {
      toast.error('خطا در به‌روزرسانی شرط');
      console.error('Error updating condition:', err);
    } finally {
      setLoading(false);
    }
  };

  // ایجاد کامپوننت ورودی بر اساس نوع
  const renderInputField = (condition) => {
    switch (condition.condition.condition_type) {
      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              id={`condition-${condition.id}`}
              checked={condition.value === 'true'}
              onChange={(e) => handleConditionChange(condition.id, e.target.checked.toString())}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <label htmlFor={`condition-${condition.id}`} className="mr-2 text-gray-700">
              {condition.condition.name}
            </label>
          </div>
        );
      
      case 'select':
        return (
          <div>
            <label htmlFor={`condition-${condition.id}`} className="block text-gray-700 mb-1">
              {condition.condition.name}
            </label>
            <select
              id={`condition-${condition.id}`}
              value={condition.value || ''}
              onChange={(e) => handleConditionChange(condition.id, e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">انتخاب کنید</option>
              {condition.condition.options_list.map((option, index) => (
                <option key={index} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        );
      
      case 'radio':
        return (
          <div>
            <span className="block text-gray-700 mb-1">{condition.condition.name}</span>
            <div className="space-y-2">
              {condition.condition.options_list.map((option, index) => (
                <div key={index} className="flex items-center">
                  <input
                    type="radio"
                    id={`condition-${condition.id}-${index}`}
                    name={`condition-${condition.id}`}
                    value={option}
                    checked={condition.value === option}
                    onChange={() => handleConditionChange(condition.id, option)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor={`condition-${condition.id}-${index}`} className="mr-2 text-gray-700">
                    {option}
                  </label>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 'color':
        return (
          <div>
            <label htmlFor={`condition-${condition.id}`} className="block text-gray-700 mb-1">
              {condition.condition.name}
            </label>
            <input
              type="color"
              id={`condition-${condition.id}`}
              value={condition.value || '#000000'}
              onChange={(e) => handleConditionChange(condition.id, e.target.value)}
              className="w-full p-1 h-10 border border-gray-300 rounded-md"
            />
          </div>
        );
      
      case 'number':
        return (
          <div>
            <label htmlFor={`condition-${condition.id}`} className="block text-gray-700 mb-1">
              {condition.condition.name}
            </label>
            <input
              type="number"
              id={`condition-${condition.id}`}
              value={condition.value || ''}
              onChange={(e) => handleConditionChange(condition.id, e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        );
      
      case 'text':
      default:
        return (
          <div>
            <label htmlFor={`condition-${condition.id}`} className="block text-gray-700 mb-1">
              {condition.condition.name}
            </label>
            <input
              type="text"
              id={`condition-${condition.id}`}
              value={condition.value || ''}
              onChange={(e) => handleConditionChange(condition.id, e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        );
    }
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
        </div>
        <div className="flex items-center">
          <div className="ml-4">
            <input
              type="checkbox"
              id={`section-completed-${userSection.id}`}
              checked={completed}
              onChange={handleCompletedChange}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              onClick={(e) => e.stopPropagation()}
            />
            <label 
              htmlFor={`section-completed-${userSection.id}`} 
              className="mr-2 text-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              تکمیل شده
            </label>
          </div>
          <span className="transform transition-transform duration-200" style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0)' }}>
            &#10095;
          </span>
        </div>
      </div>
      
      {expanded && (
        <div className="px-4 pb-4 border-t">
          {userSection.section.description && (
            <p className="text-gray-600 mb-4 mt-2">
              {userSection.section.description}
            </p>
          )}
          
          {/* نمایش ورودی‌های طراحی کاربر */}
          {designInputs && designInputs.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-700 mb-2">ورودی‌های طراحی:</h4>
              <div className="space-y-3">
                {designInputs.map(input => (
                  <div key={input.id} className="border rounded-md p-3 bg-gray-50">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{input.design_input.name || `ورودی ${input.order}`}</span>
                    </div>
                    {input.design_input.description && (
                      <p className="text-sm text-gray-500 mb-2">{input.design_input.description}</p>
                    )}
                    
                    {/* اینجا می‌توان انتخاب طرح را اضافه کرد - برای سادگی فعلاً حذف شده */}
                    {/*
                    <div>
                      <label className="block text-gray-700 mb-1">انتخاب طرح:</label>
                      <select
                        value={input.design?.id || ''}
                        onChange={(e) => handleDesignInputChange(input.id, e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">انتخاب طرح</option>
                        {input.design_input.allowed_designs.map(design => (
                          <option key={design.id} value={design.id}>
                            {design.title}
                          </option>
                        ))}
                      </select>
                    </div>
                    */}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* نمایش شرایط کاربر */}
          {conditions && conditions.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700 mb-2">شرایط و گزینه‌ها:</h4>
              <div className="space-y-4">
                {conditions.map(condition => (
                  <div key={condition.id} className="border rounded-md p-3 bg-gray-50">
                    {renderInputField(condition)}
                    
                    {condition.condition.description && (
                      <p className="text-sm text-gray-500 mt-1">{condition.condition.description}</p>
                    )}
                    
                    {condition.condition.affects_pricing && (
                      <div className="mt-1 text-sm text-green-600">
                        تأثیر در قیمت: {Number(condition.condition.price_factor).toLocaleString()} تومان
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {loading && (
            <div className="mt-3 text-center text-sm text-gray-500">
              <FaSpinner className="inline animate-spin ml-1" /> در حال ذخیره تغییرات...
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// کامپوننت اصلی ویرایش قالب کاربر
const EditUserTemplate = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [userTemplate, setUserTemplate] = useState(null);
  const [userSections, setUserSections] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
      const templateData = templateResponse.data;
      setUserTemplate(templateData);
      
      setFormData({
        title: templateData.name || templateData.template.title,
        description: templateData.description || '',
        status: templateData.status || 'DRAFT'
      });
      
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
  
  // تغییر مقادیر فرم
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // بروزرسانی بخش کاربر
  const handleSectionUpdate = async (sectionData) => {
    try {
      await axiosInstance.put(`/api/templates/user-sections/${sectionData.id}/`, sectionData);
      
      // بروزرسانی لیست بخش‌ها
      setUserSections(prevSections => 
        prevSections.map(section => 
          section.id === sectionData.id ? { ...section, ...sectionData } : section
        )
      );
    } catch (err) {
      toast.error('خطا در به‌روزرسانی بخش');
      console.error('Error updating section:', err);
    }
  };
  
  // ذخیره تغییرات قالب کاربر
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      const response = await axiosInstance.put(`/api/templates/user-templates/${id}/`, formData);
      toast.success('قالب با موفقیت به‌روزرسانی شد');
      navigate(`/user-templates/${id}`);
    } catch (err) {
      toast.error('خطا در به‌روزرسانی قالب');
      console.error('Error updating user template:', err);
    } finally {
      setSaving(false);
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
          onClick={() => navigate(`/user-templates/${id}`)}
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <FaArrowRight className="ml-1" /> بازگشت به جزئیات قالب
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">ویرایش قالب</h1>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="title" className="block text-gray-700 text-sm font-bold mb-2">
                عنوان قالب:
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="description" className="block text-gray-700 text-sm font-bold mb-2">
                توضیحات:
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="3"
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
            
            <div className="mb-6">
              <label htmlFor="status" className="block text-gray-700 text-sm font-bold mb-2">
                وضعیت:
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="DRAFT">پیش‌نویس</option>
                <option value="PENDING">در انتظار بررسی</option>
                <option value="COMPLETED">تکمیل شده</option>
              </select>
            </div>
            
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={() => navigate(`/user-templates/${id}`)}
                className="ml-4 inline-flex items-center px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                <FaTimesCircle className="ml-1" /> انصراف
              </button>
              
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {saving ? (
                  <>
                    <FaSpinner className="ml-1 animate-spin" /> در حال ذخیره
                  </>
                ) : (
                  <>
                    <FaSave className="ml-1" /> ذخیره تغییرات
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xl font-bold text-gray-800 mb-4">ویرایش بخش‌های قالب</h2>
        
        {userSections.length === 0 ? (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 text-center">
            <p className="text-gray-600">هیچ بخشی برای این قالب تعریف نشده است.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {userSections.map(userSection => (
              <UserSectionEdit 
                key={userSection.id} 
                userSection={userSection}
                onUpdate={handleSectionUpdate}
              />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default EditUserTemplate; 