import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ListBusinesses = ({ userId, isAdmin }) => {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    const fetchBusinesses = async () => {
      try {
        const params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        
        const response = await axiosInstance.get(`/api/business/businesses/?${params.toString()}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setBusinesses(response.data);
        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری کسب‌وکارها');
        setLoading(false);
      }
    };

    fetchBusinesses();
  }, [statusFilter]);

  const handleDelete = async (businessId) => {
    if (window.confirm('آیا از حذف این کسب‌وکار مطمئن هستید؟')) {
      try {
        await axiosInstance.delete(`/api/business/businesses/${businessId}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setBusinesses(businesses.filter(business => business.id !== businessId));
        toast.success('کسب‌وکار با موفقیت حذف شد');
      } catch (error) {
        toast.error('خطا در حذف کسب‌وکار');
      }
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <i className="fas fa-briefcase"></i> لیست کسب‌وکارها
        </h2>
        <div className="animate-pulse">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow mb-4">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/5"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
        <i className="fas fa-briefcase"></i> لیست کسب‌وکارها
      </h2>
      
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <label htmlFor="status-filter" className="text-sm font-medium">فیلتر بر اساس وضعیت:</label>
          <select
            id="status-filter"
            className="p-2 border rounded-md text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">همه</option>
            <option value="active">فعال</option>
            <option value="pending">در انتظار تأیید</option>
            <option value="inactive">غیرفعال</option>
          </select>
        </div>
        
        <Link
          to="/businesses/create"
          className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md flex items-center gap-2 transition-colors"
        >
          <i className="fas fa-plus"></i>
          افزودن کسب‌وکار جدید
        </Link>
      </div>
      
      {businesses.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-500">هیچ کسب‌وکاری یافت نشد</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {businesses.map((business) => (
            <motion.div
              key={business.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white p-4 rounded-lg shadow flex flex-col"
            >
              <div className="flex items-start gap-4 mb-3">
                {business.logo ? (
                  <img
                    src={business.logo}
                    alt={business.name}
                    className="w-16 h-16 object-cover rounded-md"
                  />
                ) : (
                  <div className="w-16 h-16 bg-blue-100 rounded-md flex items-center justify-center">
                    <i className="fas fa-briefcase text-blue-500 text-xl"></i>
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-1">{business.name}</h3>
                  <p className="text-sm text-gray-500">
                    وضعیت: {business.status === 'active' ? 'فعال' : business.status === 'pending' ? 'در انتظار تأیید' : 'غیرفعال'}
                  </p>
                  <p className="text-sm text-gray-500">
                    تاریخ ایجاد: {business.created_at_jalali}
                  </p>
                </div>
              </div>
              
              <div className="mt-auto pt-3 border-t flex items-center justify-between">
                <Link
                  to={`/businesses/${business.id}`}
                  className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1"
                >
                  <i className="fas fa-eye"></i> مشاهده جزئیات
                </Link>
                
                {(business.owner?.id === userId || isAdmin) && (
                  <div className="flex items-center gap-4">
                    <Link
                      to={`/businesses/edit/${business.id}`}
                      className="text-yellow-500 hover:text-yellow-700 text-sm flex items-center gap-1"
                    >
                      <i className="fas fa-edit"></i> ویرایش
                    </Link>
                    <button
                      onClick={() => handleDelete(business.id)}
                      className="text-red-500 hover:text-red-700 text-sm flex items-center gap-1"
                    >
                      <i className="fas fa-trash"></i> حذف
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ListBusinesses; 