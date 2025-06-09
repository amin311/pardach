import React, { useState, useEffect } from 'react';
import axiosInstance from './lib/axios';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';

const ReportWidget = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      setLoading(true);
      try {
        const response = await axiosInstance.get('/api/reports/?limit=5');
        setReports(response.data.results || []);
        setError(null);
      } catch (err) {
        setError('خطا در بارگذاری گزارش‌ها');
        toast.error('خطا در بارگذاری گزارش‌ها');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const getReportStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getReportTypeIcon = (type) => {
    switch (type) {
      case 'sales':
        return <i className="fas fa-chart-line text-blue-500"></i>;
      case 'user':
        return <i className="fas fa-users text-purple-500"></i>;
      case 'financial':
        return <i className="fas fa-money-bill-wave text-green-500"></i>;
      case 'inventory':
        return <i className="fas fa-warehouse text-amber-500"></i>;
      default:
        return <i className="fas fa-file-alt text-gray-500"></i>;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full flex justify-center items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-gray-600">در حال بارگذاری گزارش‌ها...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 h-full flex justify-center items-center">
        <div className="text-center text-red-500">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-lg shadow-md p-4 h-full"
    >
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
        <i className="fas fa-file-alt text-indigo-600 ml-2"></i> گزارش‌های اخیر
      </h3>
      
      {reports.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <i className="fas fa-file-alt text-gray-300 text-3xl mb-2"></i>
          <p>هیچ گزارشی یافت نشد</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map(report => (
            <Link 
              key={report.id} 
              to={`/reports/${report.id}`}
              className="block p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition"
            >
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full flex items-center justify-center ml-3 flex-shrink-0">
                  {getReportTypeIcon(report.type)}
                </div>
                <div className="flex-grow">
                  <div className="flex justify-between items-start">
                    <h4 className="font-medium text-gray-900">{report.title}</h4>
                    <span className={`text-xs px-2 py-1 rounded-full ${getReportStatusColor(report.status)}`}>
                      {report.status_display || report.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{report.description}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-gray-500">{report.created_at_jalali}</span>
                    <div className="flex items-center text-xs text-blue-600">
                      <span>مشاهده گزارش</span>
                      <i className="fas fa-chevron-left text-xs mr-1"></i>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
      
      <div className="mt-4 flex justify-between items-center">
        <Link to="/reports" className="text-blue-500 text-sm hover:underline">
          مشاهده همه گزارش‌ها
        </Link>
        <Link to="/reports/new" className="text-sm bg-blue-50 text-blue-600 px-3 py-1 rounded-md hover:bg-blue-100 transition">
          <i className="fas fa-plus ml-1"></i>
          گزارش جدید
        </Link>
      </div>
    </motion.div>
  );
};

export default ReportWidget; 