import React, { useState, useEffect } from 'react';
import axiosInstance from '../../lib/axios';
import { toast } from 'react-toastify';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Select from 'react-select';

const CreateChat = ({ userId }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    participant_ids: [],
    business_id: null
  });

  useEffect(() => {
    // دریافت لیست کاربران برای انتخاب شرکت‌کنندگان
    axiosInstance.get('/api/auth/users/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        // تبدیل داده‌ها به فرمت مناسب برای Select
        const userOptions = res.data
          .filter(user => user.id !== userId) // حذف کاربر جاری
          .map(user => ({
            value: user.id,
            label: `${user.username} (${user.email})`
          }));
        setUsers(userOptions);
      })
      .catch(err => {
        console.error('Error fetching users:', err);
        toast.error('خطا در دریافت لیست کاربران');
      });

    // دریافت لیست کسب‌وکارها
    axiosInstance.get('/api/business/businesses/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        // تبدیل داده‌ها به فرمت مناسب برای Select
        const businessOptions = res.data.map(business => ({
          value: business.id,
          label: business.name
        }));
        setBusinesses(businessOptions);
      })
      .catch(err => {
        console.error('Error fetching businesses:', err);
        toast.error('خطا در دریافت لیست کسب‌وکارها');
      });
  }, [userId]);

  const handleTitleChange = (e) => {
    setFormData({ ...formData, title: e.target.value });
  };

  const handleParticipantChange = (selectedOptions) => {
    setFormData({
      ...formData,
      participant_ids: selectedOptions.map(option => option.value)
    });
  };

  const handleBusinessChange = (selectedOption) => {
    setFormData({
      ...formData,
      business_id: selectedOption ? selectedOption.value : null
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // بررسی اعتبار فرم
    if (formData.participant_ids.length === 0) {
      toast.error('لطفاً حداقل یک شرکت‌کننده انتخاب کنید');
      return;
    }

    setLoading(true);
    
    // آماده‌سازی داده‌ها برای ارسال
    const dataToSend = {
      title: formData.title,
      participant_ids: formData.participant_ids
    };

    if (formData.business_id) {
      dataToSend.business_id = formData.business_id;
    }

    // ارسال درخواست ایجاد چت
    axiosInstance.post('/api/communication/chats/', dataToSend, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        toast.success('چت با موفقیت ایجاد شد');
        navigate(`/chats/${res.data.id}`);
      })
      .catch(err => {
        console.error('Error creating chat:', err);
        if (err.response && err.response.data) {
          // نمایش پیام‌های خطای سرور
          const errorData = err.response.data;
          if (typeof errorData === 'object') {
            Object.entries(errorData).forEach(([key, value]) => {
              if (Array.isArray(value)) {
                value.forEach(msg => toast.error(`${key}: ${msg}`));
              } else {
                toast.error(`${key}: ${value}`);
              }
            });
          } else {
            toast.error('خطا در ایجاد چت');
          }
        } else {
          toast.error('خطا در ایجاد چت');
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-2xl mx-auto"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-plus-circle"></i> ایجاد چت جدید
        </h2>
        <Link
          to="/chats"
          className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <i className="fas fa-arrow-right"></i> بازگشت به لیست چت‌ها
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit}>
          {/* عنوان چت */}
          <div className="mb-4">
            <label htmlFor="title" className="block text-gray-700 text-sm font-bold mb-2">
              عنوان چت (اختیاری)
            </label>
            <input
              type="text"
              id="title"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="مثلاً: گروه پشتیبانی"
              value={formData.title}
              onChange={handleTitleChange}
            />
          </div>

          {/* شرکت‌کنندگان */}
          <div className="mb-4">
            <label htmlFor="participants" className="block text-gray-700 text-sm font-bold mb-2">
              شرکت‌کنندگان <span className="text-red-500">*</span>
            </label>
            <Select
              id="participants"
              isMulti
              options={users}
              placeholder="کاربران را انتخاب کنید..."
              onChange={handleParticipantChange}
              className="basic-multi-select"
              classNamePrefix="select"
              isRtl={true}
            />
            <p className="text-xs text-gray-500 mt-1">
              کاربر جاری به‌طور خودکار به چت اضافه می‌شود
            </p>
          </div>

          {/* کسب‌وکار مرتبط */}
          <div className="mb-6">
            <label htmlFor="business" className="block text-gray-700 text-sm font-bold mb-2">
              کسب‌وکار مرتبط (اختیاری)
            </label>
            <Select
              id="business"
              options={businesses}
              placeholder="کسب‌وکار را انتخاب کنید..."
              onChange={handleBusinessChange}
              className="basic-single"
              classNamePrefix="select"
              isClearable
              isRtl={true}
            />
          </div>

          {/* دکمه‌های عملیات */}
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center gap-2 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  در حال ایجاد...
                </>
              ) : (
                <>
                  <i className="fas fa-check"></i>
                  ایجاد چت
                </>
              )}
            </button>
            <Link
              to="/chats"
              className="inline-block align-baseline font-bold text-sm text-gray-500 hover:text-gray-800"
            >
              انصراف
            </Link>
          </div>
        </form>
      </div>
    </motion.div>
  );
};

export default CreateChat; 