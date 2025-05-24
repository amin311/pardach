import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ListOrders = ({ userId, isAdmin }) => {
  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        
        const response = await axios.get(`/api/orders/?${params.toString()}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setOrders(response.data);
        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری سفارش‌ها');
        setLoading(false);
      }
    };

    fetchOrders();
  }, [statusFilter]);

  const handleDelete = async (orderId) => {
    if (window.confirm('آیا از حذف سفارش مطمئن هستید؟')) {
      try {
        await axios.delete(`/api/orders/${orderId}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setOrders(orders.filter(order => order.id !== orderId));
        toast.success('سفارش با موفقیت حذف شد');
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-shopping-cart"></i> لیست سفارش‌ها
        </h2>
        
        <div className="flex gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="p-2 border rounded-md text-sm"
          >
            <option value="">همه وضعیت‌ها</option>
            <option value="pending">در انتظار</option>
            <option value="processing">در حال انجام</option>
            <option value="completed">تکمیل‌شده</option>
            <option value="cancelled">لغو شده</option>
          </select>
          
          <Link
            to="/orders/create"
            className="bg-green-500 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-green-600 transition-all"
          >
            <i className="fas fa-plus"></i> سفارش جدید
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : orders.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {orders.map(order => (
            <motion.div
              key={order.id}
              className="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition-all"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-bold text-lg">سفارش #{order.id.substring(0, 8)}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1 ${getStatusClass(order.status)}`}>
                  <i className={`fas fa-${getStatusIcon(order.status)}`}></i>
                  {getStatusText(order.status)}
                </span>
              </div>
              
              <div className="mb-4">
                <p className="text-sm mb-1 flex items-center gap-2">
                  <i className="fas fa-user text-gray-500"></i>
                  <span className="font-semibold">کاربر:</span> {order.user}
                </p>
                <p className="text-sm mb-1 flex items-center gap-2">
                  <i className="fas fa-money-bill-wave text-gray-500"></i>
                  <span className="font-semibold">مبلغ کل:</span> {Number(order.total_price).toLocaleString()} تومان
                </p>
                <p className="text-sm mb-1 flex items-center gap-2">
                  <i className="fas fa-box text-gray-500"></i>
                  <span className="font-semibold">تعداد آیتم‌ها:</span> {order.items_count || 0}
                </p>
                <p className="text-sm flex items-center gap-2">
                  <i className="fas fa-calendar-alt text-gray-500"></i>
                  <span className="font-semibold">تاریخ:</span> {order.created_at}
                </p>
              </div>
              
              <div className="flex gap-2 mt-4 border-t pt-3">
                <Link 
                  to={`/orders/${order.id}`}
                  className="text-blue-500 hover:text-blue-700 transition-colors px-2 py-1 flex items-center gap-1"
                >
                  <i className="fas fa-eye"></i> مشاهده
                </Link>
                
                {(isAdmin || userId === order.user_id) && (
                  <>
                    <Link 
                      to={`/orders/edit/${order.id}`}
                      className="text-yellow-500 hover:text-yellow-700 transition-colors px-2 py-1 flex items-center gap-1"
                    >
                      <i className="fas fa-edit"></i> ویرایش
                    </Link>
                    
                    <button
                      onClick={() => handleDelete(order.id)}
                      className="text-red-500 hover:text-red-700 transition-colors px-2 py-1 flex items-center gap-1"
                    >
                      <i className="fas fa-trash"></i> حذف
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <i className="fas fa-inbox text-5xl text-gray-300 mb-4"></i>
          <p className="text-gray-500 text-lg">سفارشی یافت نشد</p>
          <Link 
            to="/orders/create"
            className="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-all"
          >
            ایجاد سفارش جدید
          </Link>
        </div>
      )}
    </motion.div>
  );
};

export default ListOrders; 