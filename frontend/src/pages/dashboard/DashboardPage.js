import React, { useState, useEffect } from 'react';
import axiosInstance from '../../lib/axios';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  Title, 
  Tooltip, 
  Legend, 
  ArcElement,
  PieController
} from 'chart.js';

// کامپوننت‌های داشبورد
import SalesDetailWidget from '../../components/dashboard/SalesDetailWidget';
import BusinessDetailWidget from '../../components/dashboard/BusinessDetailWidget';
import NotificationWidget from '../../components/dashboard/NotificationWidget';
import ReportWidget from '../../components/dashboard/ReportWidget';
import DashboardStatsWidget from '../../components/dashboard/DashboardStatsWidget';
import DashboardChartWidget from '../../components/dashboard/DashboardChartWidget';
import DashboardGuide from '../../components/dashboard/DashboardGuide';

// ثبت کامپوننت‌های مورد نیاز برای Chart.js
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  LineElement, 
  PointElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  PieController
);

const DashboardPage = ({ userId, isAdmin }) => {
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [hasSeenGuide, setHasSeenGuide] = useState(true);

  // بررسی وضعیت نمایش راهنما
  useEffect(() => {
    const checkGuideStatus = async () => {
      try {
        const response = await axiosInstance.get(`/api/main/settings/user_${userId}_dashboard_guide/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setHasSeenGuide(response.data?.value === 'true');
      } catch (error) {
        // اگر تنظیم پیدا نشد، فرض می‌کنیم کاربر راهنما را ندیده است
        setHasSeenGuide(false);
      }
    };

    if (userId) {
      checkGuideStatus();
    }
  }, [userId]);

  // دریافت داده‌های داشبورد
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get(`/api/dashboard/summary/?days=${days}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setSummary(response.data.summary);
        setCharts(response.data.charts);
        setLoading(false);
      } catch (error) {
        console.error('خطا در بارگذاری داده‌های داشبورد:', error);
        toast.error('خطا در بارگذاری داده‌های داشبورد');
        setLoading(false);
      }
    };

    fetchData();
  }, [days]);

  if (loading) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2 dashboard-header">
          <i className="fas fa-tachometer-alt"></i> داشبورد
        </h2>
        <div className="animate-pulse space-y-6">
          <div className="h-10 bg-gray-200 rounded w-1/4 mx-auto"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(5)].map((_, index) => (
              <div key={index} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-80 bg-gray-200 rounded"></div>
            <div className="h-80 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!summary || !charts) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2 dashboard-header">
          <i className="fas fa-tachometer-alt"></i> داشبورد
        </h2>
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-500">اطلاعاتی برای نمایش وجود ندارد</p>
        </div>
      </div>
    );
  }

  // تهیه داده‌های نمودار سفارش‌ها
  const orderChartData = {
    labels: charts.orders.labels,
    datasets: [
      {
        label: charts.orders.title,
        data: charts.orders.values,
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        borderColor: 'rgb(53, 162, 235)',
        borderWidth: 1,
      },
    ],
  };

  // تهیه داده‌های نمودار پرداخت‌ها
  const paymentChartData = {
    labels: charts.payments.labels,
    datasets: [
      {
        label: charts.payments.title,
        data: charts.payments.values,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  // گزینه‌های نمودار
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            family: 'Vazir, Tahoma, Arial',
          }
        }
      },
      title: {
        display: false,
      },
      tooltip: {
        bodyFont: {
          family: 'Vazir, Tahoma, Arial',
        },
        titleFont: {
          family: 'Vazir, Tahoma, Arial',
        }
      }
    },
    scales: {
      y: { 
        beginAtZero: true,
        ticks: {
          font: {
            family: 'Vazir, Tahoma, Arial',
          }
        }
      },
      x: {
        ticks: {
          font: {
            family: 'Vazir, Tahoma, Arial',
          }
        }
      }
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-6xl mx-auto"
    >
      {/* راهنمای تعاملی داشبورد */}
      <DashboardGuide userId={userId} hasSeenGuide={hasSeenGuide} />
      
      <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2 dashboard-header">
        <i className="fas fa-tachometer-alt"></i> داشبورد
      </h2>
      
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 dashboard-filters">
        <div className="flex items-center gap-2">
          <label htmlFor="days-filter" className="text-sm font-medium">نمایش داده‌های:</label>
          <select
            id="days-filter"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            className="bg-white border rounded-md p-2 text-sm"
          >
            <option value="7">۷ روز اخیر</option>
            <option value="30">۳۰ روز اخیر</option>
            <option value="90">۹۰ روز اخیر</option>
            <option value="180">۶ ماه اخیر</option>
            <option value="365">یک سال اخیر</option>
          </select>
        </div>
        
        {isAdmin && (
          <button
            onClick={() => toast.info('در حال بروزرسانی داده‌ها...')}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md flex items-center gap-2 transition-colors text-sm"
          >
            <i className="fas fa-sync-alt"></i>
            بروزرسانی داده‌ها
          </button>
        )}
      </div>
      
      {/* کامپوننت آمار داشبورد */}
      <div className="dashboard-stats mb-8">
        <DashboardStatsWidget 
          stats={[
            { title: "سفارش‌ها", value: summary.order_count, icon: "shopping-cart", color: "blue", suffix: "" },
            { title: "مجموع فروش", value: summary.total_sales, icon: "money-bill-wave", color: "green", suffix: " تومان" },
            { title: "پرداخت‌ها", value: summary.payment_count, icon: "credit-card", color: "purple", suffix: "" },
            { title: "اعلانات جدید", value: summary.unread_notifications, icon: "bell", color: "yellow", suffix: "" },
            { title: "گزارش‌ها", value: summary.report_count, icon: "chart-bar", color: "red", suffix: "" },
            { title: "مجموع پرداخت", value: summary.total_payments, icon: "wallet", color: "indigo", suffix: " تومان" }
          ]}
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* نمودار سفارش‌ها */}
        <div className="orders-chart">
          <DashboardChartWidget
            title={charts.orders.title}
            type="bar"
            data={orderChartData}
            options={chartOptions}
            description="نمایش میزان سفارش‌های روزانه در بازه انتخاب شده"
            icon="chart-bar"
            color="blue"
          />
        </div>
        
        {/* نمودار پرداخت‌ها */}
        <div className="payments-chart">
          <DashboardChartWidget
            title={charts.payments.title}
            type="line"
            data={paymentChartData}
            options={chartOptions}
            description="نمایش میزان پرداخت‌های روزانه در بازه انتخاب شده"
            icon="chart-line"
            color="green"
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div>
          <SalesDetailWidget days={days} />
        </div>
        
        <div>
          <BusinessDetailWidget days={days} />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div>
          <NotificationWidget />
        </div>
        
        <div>
          <ReportWidget />
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <i className="fas fa-info-circle text-blue-600"></i>
          راهنما
        </h3>
        
        <div className="text-sm text-gray-600 space-y-2">
          <p>• تمامی آمار و اطلاعات نمایش داده شده مربوط به <span className="font-bold">{days} روز</span> گذشته می‌باشد.</p>
          <p>• مبالغ به تومان نمایش داده می‌شوند.</p>
          <p>• برای دسترسی به گزارش‌های تفصیلی، به بخش <a href="/reports" className="text-blue-600 hover:underline">گزارش‌ها</a> مراجعه نمایید.</p>
          <p>• برای نمایش مجدد راهنمای تعاملی، روی دکمه راهنما در پایین سمت چپ صفحه کلیک کنید.</p>
        </div>
      </div>
    </motion.div>
  );
};

export default DashboardPage; 