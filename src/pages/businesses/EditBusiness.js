import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const EditBusiness = ({ userId, isAdmin }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'pending',
    logo: null
  });
  const [logoPreview, setLogoPreview] = useState(null);
  const [existingLogo, setExistingLogo] = useState(null);
  
  useEffect(() => {
    const fetchBusinessData = async () => {
      try {
        const response = await axios.get(`/api/business/businesses/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        const business = response.data;
        setFormData({
          name: business.name || '',
          description: business.description || '',
          status: business.status || 'pending',
          logo: null
        });
        
        if (business.logo) {
          setExistingLogo(business.logo);
        }
        
        setFetchLoading(false);
      } catch (error) {
        console.error('Error fetching business data:', error);
        toast.error('خطا در دریافت اطلاعات کسب‌وکار');
        
        // در صورت خطا 404 یا 403 کاربر به صفحه لیست برگردانده شود
        if (error.response && (error.response.status === 404 || error.response.status === 403)) {
          navigate('/businesses');
        }
      }
    };
    
    fetchBusinessData();
  }, [id, navigate]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({
        ...formData,
        logo: file
      });
      
      // ایجاد پیش‌نمایش فایل
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result);
      };
      reader.readAsDataURL(file);
      
      // حذف لوگوی قبلی در پیش‌نمایش
      setExistingLogo(null);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('status', formData.status);
      
      if (formData.logo) {
        formDataToSend.append('logo', formData.logo);
      }
      
      await axios.put(`/api/business/businesses/${id}/`, formDataToSend, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast.success('کسب‌وکار با موفقیت به‌روزرسانی شد');
      navigate(`/businesses/${id}`);
    } catch (error) {
      console.error('Error updating business:', error);
      if (error.response && error.response.data) {
        // نمایش خطاهای دریافتی از سرور
        if (typeof error.response.data === 'object') {
          Object.entries(error.response.data).forEach(([field, errors]) => {
            if (Array.isArray(errors)) {
              errors.forEach(err => toast.error(`${field}: ${err}`));
            } else {
              toast.error(`${field}: ${errors}`);
            }
          });
        } else {
          toast.error('خطا در به‌روزرسانی کسب‌وکار');
        }
      } else {
        toast.error('خطا در به‌روزرسانی کسب‌وکار');
      }
    } finally {
      setLoading(false);
    }
  };
  
  if (fetchLoading) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-10 bg-gray-200 rounded mb-4"></div>
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-28 bg-gray-200 rounded mb-4"></div>
            <div className="h-10 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-2xl mx-auto"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-edit"></i> ویرایش کسب‌وکار
        </h2>
        <div className="flex items-center gap-3">
          <Link
            to={`/businesses/${id}`}
            className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <i className="fas fa-eye"></i> مشاهده جزئیات
          </Link>
          <Link
            to="/businesses"
            className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <i className="fas fa-arrow-right"></i> بازگشت به لیست
          </Link>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
              نام کسب‌وکار <span className="text-red-500">*</span>
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="name"
              type="text"
              name="name"
              placeholder="نام کسب‌وکار"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
              توضیحات
            </label>
            <textarea
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="description"
              name="description"
              placeholder="توضیحات کسب‌وکار"
              rows="4"
              value={formData.description}
              onChange={handleChange}
            ></textarea>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="status">
              وضعیت
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="pending">در انتظار تأیید</option>
              <option value="active">فعال</option>
              <option value="inactive">غیرفعال</option>
            </select>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="logo">
              لوگو
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="logo"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
            
            {existingLogo && !logoPreview && (
              <div className="mt-2">
                <p className="text-sm text-gray-500 mb-1">لوگوی فعلی:</p>
                <img
                  src={existingLogo}
                  alt="Current Logo"
                  className="w-32 h-32 object-cover rounded-md border"
                />
              </div>
            )}
            
            {logoPreview && (
              <div className="mt-2">
                <p className="text-sm text-gray-500 mb-1">لوگوی جدید:</p>
                <img
                  src={logoPreview}
                  alt="New Logo Preview"
                  className="w-32 h-32 object-cover rounded-md border"
                />
              </div>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <button
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center gap-2 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  در حال به‌روزرسانی...
                </>
              ) : (
                <>
                  <i className="fas fa-save"></i>
                  ذخیره تغییرات
                </>
              )}
            </button>
            <Link
              className="inline-block align-baseline font-bold text-sm text-gray-500 hover:text-gray-800"
              to={`/businesses/${id}`}
            >
              انصراف
            </Link>
          </div>
        </form>
      </div>
    </motion.div>
  );
};

export default EditBusiness; 