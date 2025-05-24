import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaShoppingBag, FaCheck, FaSpinner, FaExclamationCircle, FaClock, FaChevronDown, FaChevronUp } from 'react-icons/fa';

/**
 * نمایش حالت سفارش با رنگ و آیکون متناسب
 * @param {String} status - وضعیت سفارش
 */
const OrderStatusBadge = ({ status }) => {
  // تعیین رنگ و آیکون بر اساس وضعیت
  let color, icon, text;
  
  switch (status) {
    case 'completed':
      color = 'bg-green-100 text-green-800';
      icon = <FaCheck className="text-green-500" />;
      text = 'تکمیل شده';
      break;
    case 'processing':
      color = 'bg-blue-100 text-blue-800';
      icon = <FaSpinner className="text-blue-500 animate-spin" />;
      text = 'در حال پردازش';
      break;
    case 'cancelled':
      color = 'bg-red-100 text-red-800';
      icon = <FaExclamationCircle className="text-red-500" />;
      text = 'لغو شده';
      break;
    case 'pending':
    default:
      color = 'bg-yellow-100 text-yellow-800';
      icon = <FaClock className="text-yellow-500" />;
      text = 'در انتظار';
      break;
  }

  return (
    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      <span className="mr-1">{icon}</span>
      {text}
    </div>
  );
};

/**
 * کامپوننت نمایش سفارش‌های اخیر
 * @param {Array} orders - لیست سفارش‌ها
 */
const RecentOrdersWidget = ({ orders = [] }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* هدر ویجت */}
      <div 
        className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4 flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2 text-white">
          <FaShoppingBag className="text-xl" />
          <h2 className="text-lg font-bold">سفارش‌های اخیر</h2>
        </div>
        <div className="text-white">
          {expanded ? <FaChevronUp /> : <FaChevronDown />}
        </div>
      </div>

      {/* محتوای ویجت */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {orders.length > 0 ? (
              <div className="divide-y">
                {orders.map((order, index) => (
                  <div key={order.id || index} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <Link to={`/orders/${order.id}`} className="font-medium text-blue-600 hover:text-blue-800">
                        سفارش #{order.id}
                      </Link>
                      <OrderStatusBadge status={order.status} />
                    </div>
                    
                    <div className="flex justify-between items-center text-sm">
                      <div className="text-gray-600">
                        <span className="inline-block ml-2">تاریخ:</span>
                        <span>{order.created_at}</span>
                      </div>
                      <div className="font-bold text-gray-800">
                        {new Intl.NumberFormat('fa-IR').format(order.total_price)} تومان
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <FaShoppingBag className="mx-auto text-3xl text-gray-300 mb-2" />
                <p>سفارشی وجود ندارد</p>
              </div>
            )}

            {/* فوتر */}
            {orders.length > 0 && (
              <div className="p-3 bg-gray-50 text-center">
                <Link to="/orders" className="text-sm text-blue-600 hover:text-blue-800">
                  مشاهده همه سفارش‌ها
                </Link>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RecentOrdersWidget; 