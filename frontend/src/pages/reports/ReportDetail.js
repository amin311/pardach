import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';
import { 
  FaChartLine, FaChartPie, FaChartBar, FaFileAlt, 
  FaDownload, FaEdit, FaTrash, FaShare, FaArrowRight
} from 'react-icons/fa';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell
} from 'recharts';

const ReportDetail = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // تابع نمایش آیکون مناسب برای هر نوع گزارش
  const getReportIcon = (type) => {
    switch (type) {
      case 'sales':
        return <FaChartLine className="text-blue-600 text-2xl" />;
      case 'profit':
        return <FaChartBar className="text-green-600 text-2xl" />;
      case 'user_activity':
        return <FaChartPie className="text-purple-600 text-2xl" />;
      case 'business_performance':
        return <FaChartBar className="text-orange-600 text-2xl" />;
      default:
        return <FaFileAlt className="text-gray-600 text-2xl" />;
    }
  };

  // دریافت نام فارسی نوع گزارش
  const getReportTypeName = (type) => {
    const types = {
      'sales': 'فروش',
      'profit': 'سود',
      'user_activity': 'فعالیت کاربران',
      'business_performance': 'عملکرد کسب‌وکار'
    };
    return types[type] || type;
  };

  // بارگیری داده‌های گزارش
  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(`/api/reports/${reportId}/`);
      setReport(response.data);
    } catch (error) {
      console.error('Error fetching report:', error);
      setError('خطا در بارگیری گزارش');
      toast.error('خطا در بارگیری گزارش');
    } finally {
      setLoading(false);
    }
  };

  // حذف گزارش
  const deleteReport = async () => {
    if (!window.confirm('آیا از حذف این گزارش اطمینان دارید؟ این عملیات غیرقابل بازگشت است.')) {
      return;
    }
    
    try {
      await axiosInstance.delete(`/api/reports/${reportId}/`);
      toast.success('گزارش با موفقیت حذف شد');
      navigate('/reports');
    } catch (error) {
      console.error('Error deleting report:', error);
      toast.error('خطا در حذف گزارش');
    }
  };

  // دانلود گزارش
  const downloadReport = () => {
    if (!report) return;
    
    // ساخت فایل JSON برای دانلود
    const data = JSON.stringify(report.data, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const href = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = href;
    link.download = `${report.title.replace(/\s+/g, '_')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(href);
  };

  // اشتراک‌گذاری گزارش
  const shareReport = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('لینک گزارش در کلیپ‌بورد کپی شد');
  };

  // نمایش نمودار مناسب بر اساس نوع گزارش
  const renderChart = () => {
    if (!report || !report.data) return null;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
    
    switch (report.type) {
      case 'sales':
      case 'profit':
        // نمودار خطی برای فروش و سود
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={report.data.data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                name={report.type === 'sales' ? 'مبلغ فروش' : 'سود'} 
                stroke={report.type === 'sales' ? '#0088FE' : '#00C49F'} 
                activeDot={{ r: 8 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        );
        
      case 'user_activity':
        // نمودار دایره‌ای برای فعالیت کاربران
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={report.data.data}
                cx="50%"
                cy="50%"
                labelLine={true}
                outerRadius={150}
                fill="#8884d8"
                dataKey="value"
                nameKey="label"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {report.data.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => value} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
        
      case 'business_performance':
        // نمودار رادار برای عملکرد کسب‌وکار
        return (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={report.data.data}>
              <PolarGrid />
              <PolarAngleAxis dataKey="label" />
              <PolarRadiusAxis angle={30} domain={[0, 'auto']} />
              <Radar name="عملکرد" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              <Legend />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        );
        
      default:
        // نمودار میله‌ای به صورت پیش‌فرض
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={report.data?.data || []}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" name="مقدار" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  // بارگیری داده‌ها در زمان لود کامپوننت
  useEffect(() => {
    fetchReport();
  }, [reportId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 p-4 rounded-lg text-center">
          <div className="text-red-600 text-lg mb-2">{error}</div>
          <button
            onClick={() => navigate('/reports')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center mx-auto"
          >
            <FaArrowRight className="ml-2" />
            بازگشت به لیست گزارش‌ها
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 p-4 rounded-lg text-center">
          <div className="text-yellow-600 text-lg mb-2">گزارش یافت نشد</div>
          <button
            onClick={() => navigate('/reports')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center mx-auto"
          >
            <FaArrowRight className="ml-2" />
            بازگشت به لیست گزارش‌ها
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* هدر و اطلاعات گزارش */}
      <div className="flex flex-col md:flex-row justify-between items-start mb-6">
        <div>
          <div className="flex items-center mb-2">
            <button
              onClick={() => navigate('/reports')}
              className="text-blue-600 hover:text-blue-800 ml-2"
            >
              <FaArrowRight />
            </button>
            <div className="flex items-center">
              {getReportIcon(report.type)}
              <h1 className="text-2xl font-bold text-gray-800 mr-2">{report.title}</h1>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="bg-gray-100 text-gray-800 text-sm font-medium px-2.5 py-0.5 rounded">
              {getReportTypeName(report.type)}
            </span>
            {report.is_public && (
              <span className="bg-green-100 text-green-800 text-sm font-medium px-2.5 py-0.5 rounded">
                عمومی
              </span>
            )}
            {report.category && (
              <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded">
                {report.category.name}
              </span>
            )}
          </div>
          
          <div className="text-sm text-gray-600">
            <p className="mb-1">
              <span className="font-medium">تاریخ تولید:</span> {report.jalali_generated_at}
            </p>
            {report.business && (
              <p className="mb-1">
                <span className="font-medium">کسب‌وکار:</span> {report.business.name}
              </p>
            )}
            <p>
              <span className="font-medium">ایجاد شده توسط:</span> {report.user.full_name || report.user.username}
            </p>
          </div>
        </div>
        
        <div className="flex gap-2 mt-4 md:mt-0">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={downloadReport}
            className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg"
          >
            <FaDownload className="ml-1" />
            دانلود
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={shareReport}
            className="flex items-center px-3 py-2 bg-green-600 text-white rounded-lg"
          >
            <FaShare className="ml-1" />
            اشتراک‌گذاری
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={deleteReport}
            className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg"
          >
            <FaTrash className="ml-1" />
            حذف
          </motion.button>
        </div>
      </div>

      {/* نمودار */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-md mb-6"
      >
        <h2 className="text-xl font-semibold text-gray-800 mb-4">نمودار</h2>
        {renderChart()}
      </motion.div>

      {/* داده‌های خام */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-4 rounded-lg shadow-md"
      >
        <h2 className="text-xl font-semibold text-gray-800 mb-4">داده‌های خام</h2>
        <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
          <pre className="text-sm">{JSON.stringify(report.data, null, 2)}</pre>
        </div>
      </motion.div>
    </div>
  );
};

export default ReportDetail; 