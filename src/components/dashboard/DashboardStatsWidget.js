import React from 'react';
import { motion } from 'framer-motion';
import { FaShoppingCart, FaMoneyBillWave, FaCreditCard, FaBell, FaChartBar } from 'react-icons/fa';

/**
 * کامپوننت ویجت آمار داشبورد 
 * نمایش آمار خلاصه از سفارش‌ها، پرداخت‌ها و اعلان‌ها
 * @param {Object} summary - خلاصه داده‌های داشبورد
 */
const DashboardStatsWidget = ({ summary }) => {
  if (!summary) return null;

  // آرایه‌ای از آیتم‌های آماری با آیکون و رنگ مشخص
  const statItems = [
    {
      title: 'تعداد سفارش‌ها',
      value: summary.order_count.toLocaleString('fa-IR'),
      icon: <FaShoppingCart className="text-3xl text-blue-500" />,
      color: 'from-blue-500 to-blue-600',
      suffix: 'سفارش'
    },
    {
      title: 'مجموع فروش',
      value: summary.total_sales.toLocaleString('fa-IR'),
      icon: <FaMoneyBillWave className="text-3xl text-green-500" />,
      color: 'from-green-500 to-green-600',
      suffix: 'تومان'
    },
    {
      title: 'تعداد پرداخت‌ها',
      value: summary.payment_count.toLocaleString('fa-IR'),
      icon: <FaCreditCard className="text-3xl text-purple-500" />,
      color: 'from-purple-500 to-purple-600',
      suffix: 'پرداخت'
    },
    {
      title: 'اعلانات خوانده‌نشده',
      value: summary.unread_notifications.toLocaleString('fa-IR'),
      icon: <FaBell className="text-3xl text-orange-500" />,
      color: 'from-orange-500 to-orange-600',
      suffix: 'اعلان'
    },
    {
      title: 'تعداد گزارش‌ها',
      value: summary.report_count.toLocaleString('fa-IR'),
      icon: <FaChartBar className="text-3xl text-red-500" />,
      color: 'from-red-500 to-red-600',
      suffix: 'گزارش'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-6 dashboard-stats">
      {statItems.map((item, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          whileHover={{ y: -5, scale: 1.03 }}
          className={`p-4 rounded-lg shadow-md overflow-hidden relative bg-gradient-to-br ${item.color} text-white`}
        >
          <div className="absolute opacity-10 right-2 top-2 text-5xl">
            {item.icon}
          </div>
          <div className="flex items-start gap-4 relative z-10">
            <div className="bg-white/20 p-3 rounded-full">
              {item.icon}
            </div>
            <div>
              <p className="text-sm font-bold">{item.title}</p>
              <p className="text-xl font-bold mt-1">{item.value}</p>
              <p className="text-xs opacity-70 mt-1">{item.suffix}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default DashboardStatsWidget; 