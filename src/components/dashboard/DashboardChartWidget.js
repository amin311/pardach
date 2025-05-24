import React from 'react';
import { motion } from 'framer-motion';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';

// ثبت نام کامپوننت‌های چارت
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  ArcElement,
  Title, 
  Tooltip, 
  Legend
);

/**
 * کامپوننت ویجت نمودار داشبورد
 * نمایش نمودارهای تعاملی با قابلیت تغییر نوع نمودار
 * @param {string} title - عنوان نمودار
 * @param {string} type - نوع نمودار (bar, line, pie)
 * @param {Object} data - داده‌های نمودار
 * @param {Object} options - تنظیمات نمودار
 */
const DashboardChartWidget = ({ title, type, data, options }) => {
  // انتخاب نوع نمودار
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={data} options={options} />;
      case 'line':
        return <Line data={data} options={options} />;
      case 'pie':
        return <Pie data={data} options={options} />;
      default:
        return <Bar data={data} options={options} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-4 bg-white rounded-lg shadow-md"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-gray-800">{title}</h3>
        <div className="text-sm px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
          {type === 'bar' && 'نمودار ستونی'}
          {type === 'line' && 'نمودار خطی'}
          {type === 'pie' && 'نمودار دایره‌ای'}
        </div>
      </div>
      
      <div className="h-64">
        {renderChart()}
      </div>
      
      {/* توضیحات بیشتر برای کاربران کم‌سواد */}
      <div className="mt-4 border-t pt-2 text-xs text-gray-500">
        <p>
          {type === 'bar' && 'این نمودار ستونی مقادیر را با ارتفاع ستون‌ها نشان می‌دهد. ستون‌های بلندتر مقادیر بیشتر را نشان می‌دهند.'}
          {type === 'line' && 'این نمودار خطی روند تغییرات را در طول زمان نشان می‌دهد. خط بالارونده نشان‌دهنده افزایش و خط پایین‌رونده نشان‌دهنده کاهش است.'}
          {type === 'pie' && 'این نمودار دایره‌ای سهم هر بخش را از کل نشان می‌دهد. بخش‌های بزرگتر نشان‌دهنده مقادیر بیشتر هستند.'}
        </p>
        <div className="flex items-center gap-1 mt-1">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>برای مشاهده جزئیات، نشانگر را روی نمودار حرکت دهید</span>
        </div>
      </div>
    </motion.div>
  );
};

export default DashboardChartWidget; 