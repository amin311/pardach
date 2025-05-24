import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const DetailOrder = ({ userId, isAdmin }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/orders/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setOrder(response.data);
        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری اطلاعات سفارش');
        setLoading(false);
        navigate('/orders');
      }
    };

    fetchOrder();
  }, [id, navigate]);

  const handleDelete = async () => {
    if (window.confirm('آیا از حذف این سفارش مطمئن هستید؟')) {
      try {
        await axios.delete(`/api/orders/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        toast.success('سفارش با موفقیت حذف شد');
        navigate('/orders');
      } catch (error) {
        toast.error('خطا در حذف سفارش');
      }
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return 'clock';
      case 'processing': return 'spinner';
      case 'completed': return 'check-circle';
      case 'cancelled': return 'times-circle';
      default: return 'question-circle';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'در انتظار';
      case 'processing': return 'در حال انجام';
      case 'completed': return 'تکمیل‌شده';
      case 'cancelled': return 'لغو شده';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="p-6 max-w-4xl mx-auto text-center">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <i className="fas fa-exclamation-circle text-red-500 text-5xl mb-4"></i>
          <p className="text-xl mb-4">سفارش موردنظر یافت نشد</p>
          <Link
            to="/orders"
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-all"
          >
            بازگشت به لیست سفارش‌ها
          </Link>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-shopping-cart"></i> جزئیات سفارش
        </h2>
        
        <div className="flex gap-2">
          <Link
            to="/orders"
            className="bg-gray-500 text-white px-3 py-1 rounded-md flex items-center gap-1 hover:bg-gray-600 transition-all"
          >
            <i className="fas fa-arrow-right"></i> بازگشت
          </Link>
          
          {(isAdmin || userId === order.user_id) && (
            <>
              <Link
                to={`/orders/edit/${order.id}`}
                className="bg-yellow-500 text-white px-3 py-1 rounded-md flex items-center gap-1 hover:bg-yellow-600 transition-all"
              >
                <i className="fas fa-edit"></i> ویرایش
              </Link>
              
              <button
                onClick={handleDelete}
                className="bg-red-500 text-white px-3 py-1 rounded-md flex items-center gap-1 hover:bg-red-600 transition-all"
              >
                <i className="fas fa-trash"></i> حذف
              </button>
            </>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <h3 className="font-bold text-xl">سفارش #{order.id.substring(0, 8)}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1 ${getStatusClass(order.status)}`}>
              <i className={`fas fa-${getStatusIcon(order.status)}`}></i>
              {getStatusText(order.status)}
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-bold text-lg mb-2 border-b pb-2">اطلاعات سفارش</h4>
              <p className="mb-2 flex items-center gap-2">
                <i className="fas fa-user text-gray-500"></i>
                <span className="font-semibold">کاربر:</span> {order.user}
              </p>
              <p className="mb-2 flex items-center gap-2">
                <i className="fas fa-money-bill-wave text-gray-500"></i>
                <span className="font-semibold">مبلغ کل:</span> {Number(order.total_price).toLocaleString()} تومان
              </p>
              <p className="mb-2 flex items-center gap-2">
                <i className="fas fa-calendar-alt text-gray-500"></i>
                <span className="font-semibold">تاریخ ایجاد:</span> {order.created_at}
              </p>
              <p className="mb-2 flex items-center gap-2">
                <i className="fas fa-calendar-check text-gray-500"></i>
                <span className="font-semibold">آخرین بروزرسانی:</span> {order.updated_at}
              </p>
            </div>
            
            <div>
              <h4 className="font-bold text-lg mb-2 border-b pb-2">یادداشت‌ها</h4>
              <p className="bg-gray-50 p-3 rounded-md min-h-[100px]">
                {order.notes || 'بدون یادداشت'}
              </p>
            </div>
          </div>
          
          <div>
            <h4 className="font-bold text-lg mb-4 border-b pb-2 flex items-center gap-2">
              <i className="fas fa-box"></i> آیتم‌های سفارش
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">{order.items?.length || 0} آیتم</span>
            </h4>
            
            {order.items?.length > 0 ? (
              <div className="grid grid-cols-1 gap-4">
                {order.items.map(item => (
                  <motion.div
                    key={item.id}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-100"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        {item.design && (
                          <h5 className="font-bold text-md mb-1 flex items-center gap-2">
                            <i className="fas fa-palette text-blue-500"></i> طرح: {item.design.title}
                          </h5>
                        )}
                        
                        {item.user_template && (
                          <h5 className="font-bold text-md mb-1 flex items-center gap-2">
                            <i className="fas fa-file-alt text-green-500"></i> قالب: {item.user_template.name}
                          </h5>
                        )}
                        
                        <div className="mt-2 grid grid-cols-2 gap-x-4 text-sm">
                          <p className="flex items-center gap-1">
                            <i className="fas fa-hashtag text-gray-500"></i>
                            <span className="font-semibold">تعداد:</span> {item.quantity}
                          </p>
                          <p className="flex items-center gap-1">
                            <i className="fas fa-tag text-gray-500"></i>
                            <span className="font-semibold">قیمت:</span> {Number(item.price).toLocaleString()} تومان
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {item.design && (
                          <Link
                            to={`/designs/${item.design.id}`}
                            className="text-blue-500 hover:text-blue-700 transition-colors"
                          >
                            <i className="fas fa-external-link-alt"></i>
                          </Link>
                        )}
                        
                        {item.user_template && (
                          <Link
                            to={`/user-templates/${item.user_template.id}`}
                            className="text-green-500 hover:text-green-700 transition-colors"
                          >
                            <i className="fas fa-external-link-alt"></i>
                          </Link>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center p-8 bg-gray-50 rounded-lg">
                <i className="fas fa-box-open text-4xl text-gray-300 mb-2"></i>
                <p className="text-gray-500">هیچ آیتمی برای این سفارش وجود ندارد</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DetailOrder; 