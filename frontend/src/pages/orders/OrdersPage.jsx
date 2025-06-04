import React, { useState, useEffect } from 'react';
import axios from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // بارگذاری لیست سفارش‌ها در لود اولیه صفحه
  useEffect(() => {
    fetchOrders();
  }, []);

  // دریافت لیست سفارش‌ها از سرور
  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/orders/');
      setOrders(response.data);
    } catch (error) {
      toast.error('خطا در بارگذاری سفارش‌ها');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // حذف سفارش با تأیید قبلی
  const handleDelete = async (orderId) => {
    if (window.confirm('آیا از حذف سفارش مطمئن هستید؟')) {
      try {
        await axios.delete(`/api/orders/${orderId}/`);
        setOrders(orders.filter(order => order.id !== orderId));
        toast.success('سفارش با موفقیت حذف شد');
      } catch (error) {
        toast.error('خطا در حذف سفارش');
        console.error(error);
      }
    }
  };

  // تبدیل تاریخ به شمسی
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
  };

  // نمایش وضعیت سفارش
  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { label: 'در انتظار', color: 'bg-yellow-500' },
      'confirmed': { label: 'تأیید شده', color: 'bg-green-500' },
      'in_progress': { label: 'در حال انجام', color: 'bg-blue-500' },
      'completed': { label: 'تکمیل شده', color: 'bg-purple-500' },
      'cancelled': { label: 'لغو شده', color: 'bg-red-500' },
    };
    
    const statusInfo = statusMap[status] || { label: 'نامشخص', color: 'bg-gray-500' };
    
    return (
      <span className={`px-2 py-1 text-xs text-white rounded ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    );
  };

  // فیلتر سفارش‌ها
  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.id.toString().includes(search) ||
                         order.customer?.username?.toLowerCase().includes(search.toLowerCase()) ||
                         order.business?.name?.toLowerCase().includes(search.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

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
        <span className="text-3xl">📋</span>
        مدیریت سفارش‌ها
      </h1>
      
      <div className="mb-6 flex flex-wrap gap-4 justify-between items-center">
        {/* جستجو */}
        <div className="relative flex-grow max-w-xl">
          <input
            type="text"
            className="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            placeholder="جستجو بر اساس شماره سفارش، کاربر یا کسب‌وکار..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <span className="absolute left-3 top-3 text-gray-400">🔍</span>
        </div>
        
        {/* فیلتر وضعیت */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="pending">در انتظار</option>
          <option value="confirmed">تأیید شده</option>
          <option value="in_progress">در حال انجام</option>
          <option value="completed">تکمیل شده</option>
          <option value="cancelled">لغو شده</option>
        </select>
        
        {/* دکمه افزودن سفارش */}
        <Link
          to="/orders/create"
          className="bg-green-500 text-white py-3 px-6 rounded-lg flex items-center gap-2 hover:bg-green-600 transition duration-200"
        >
          <span>➕</span>
          ایجاد سفارش جدید
        </Link>
      </div>
      
      {/* لیست سفارش‌ها */}
      {filteredOrders.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-5xl mb-4">📋</div>
          <p>هیچ سفارشی یافت نشد</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    شماره سفارش
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    مشتری
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    کسب‌وکار
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تاریخ ایجاد
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredOrders.map(order => (
                  <motion.tr
                    key={order.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.customer?.username || 'نامشخص'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.business?.name || 'نامشخص'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(order.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(order.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <Link
                          to={`/orders/${order.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          مشاهده
                        </Link>
                        <Link
                          to={`/orders/edit/${order.id}`}
                          className="text-yellow-600 hover:text-yellow-900"
                        >
                          ویرایش
                        </Link>
                        <button
                          onClick={() => handleDelete(order.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          حذف
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrdersPage; 