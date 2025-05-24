import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import Slider from 'react-slick';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import { motion } from 'framer-motion';

const OrderWidget = ({ userId }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecentOrders = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/orders/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        // دریافت 5 سفارش اخیر
        setOrders(response.data.slice(0, 5));
        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری سفارش‌ها');
        setLoading(false);
      }
    };

    fetchRecentOrders();
  }, []);

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  const sliderSettings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: orders.length < 3 ? orders.length : 3,
    slidesToScroll: 1,
    rtl: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: orders.length < 2 ? orders.length : 2,
          slidesToScroll: 1,
        }
      },
      {
        breakpoint: 640,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
  };

  return (
    <motion.div 
      className="bg-white rounded-lg shadow-md p-4 mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <i className="fas fa-shopping-cart text-blue-500"></i> سفارش‌های اخیر
        </h3>
        
        <Link to="/orders" className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1">
          مشاهده همه <i className="fas fa-chevron-left"></i>
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : orders.length > 0 ? (
        <Slider {...sliderSettings} className="orders-slider">
          {orders.map(order => (
            <div key={order.id} className="px-2">
              <div className="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-all">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold">سفارش #{order.id.substring(0, 6)}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${getStatusClass(order.status)}`}>
                    {getStatusText(order.status)}
                  </span>
                </div>
                
                <p className="text-sm mb-1 flex items-center gap-1">
                  <i className="fas fa-money-bill-wave text-gray-400"></i>
                  <span>{Number(order.total_price).toLocaleString()} تومان</span>
                </p>
                
                <p className="text-sm mb-1 flex items-center gap-1">
                  <i className="fas fa-box text-gray-400"></i>
                  <span>{order.items_count || 0} آیتم</span>
                </p>
                
                <p className="text-sm mb-2 flex items-center gap-1">
                  <i className="fas fa-calendar-alt text-gray-400"></i>
                  <span>{order.created_at}</span>
                </p>
                
                <Link 
                  to={`/orders/${order.id}`} 
                  className="text-blue-500 hover:text-blue-700 text-sm flex items-center justify-center w-full mt-2 border-t pt-2"
                >
                  مشاهده جزئیات <i className="fas fa-chevron-left mr-1"></i>
                </Link>
              </div>
            </div>
          ))}
        </Slider>
      ) : (
        <div className="text-center py-8">
          <i className="fas fa-box-open text-gray-300 text-4xl mb-2"></i>
          <p className="text-gray-500">سفارشی وجود ندارد</p>
          <Link
            to="/orders/create"
            className="mt-3 inline-block bg-blue-500 text-white text-sm px-4 py-2 rounded hover:bg-blue-600 transition-all"
          >
            ایجاد سفارش جدید
          </Link>
        </div>
      )}
    </motion.div>
  );
};

export default OrderWidget; 