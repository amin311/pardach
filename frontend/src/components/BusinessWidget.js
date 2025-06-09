import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import { motion } from 'framer-motion';

const BusinessWidget = ({ userId }) => {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActiveBusinesses = async () => {
      try {
        const response = await axiosInstance.get('/api/business/businesses/?status=active', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        // حداکثر 5 کسب‌وکار نمایش داده شود
        setBusinesses(response.data.slice(0, 5));
        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری کسب‌وکارها');
        setLoading(false);
      }
    };

    fetchActiveBusinesses();
  }, []);

  const sliderSettings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: businesses.length < 3 ? businesses.length : 3,
    slidesToScroll: 1,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: businesses.length < 2 ? businesses.length : 2,
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

  if (loading) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md animate-pulse">
        <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
        <div className="h-24 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!businesses.length) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
          <i className="fas fa-briefcase text-blue-500"></i> کسب‌وکارهای فعال
        </h3>
        <p className="text-gray-500 text-sm">کسب‌وکاری وجود ندارد</p>
        <Link to="/businesses/create" className="mt-2 text-blue-500 text-sm block">
          ایجاد کسب‌وکار جدید
        </Link>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-4 bg-white rounded-lg shadow-md"
    >
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <i className="fas fa-briefcase text-blue-500"></i> کسب‌وکارهای فعال
      </h3>
      
      <Slider {...sliderSettings}>
        {businesses.map(business => (
          <div key={business.id} className="px-2">
            <Link to={`/businesses/${business.id}`}>
              <motion.div 
                whileHover={{ scale: 1.03 }}
                className="border rounded-lg p-3 h-36 flex flex-col items-center justify-center text-center"
              >
                {business.logo ? (
                  <img 
                    src={business.logo} 
                    alt={business.name} 
                    className="w-16 h-16 object-cover rounded-full mb-2"
                  />
                ) : (
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                    <i className="fas fa-briefcase text-blue-500 text-xl"></i>
                  </div>
                )}
                <h4 className="font-bold text-sm mb-1">{business.name}</h4>
                <p className="text-xs text-gray-500 truncate w-full">
                  {business.created_at_jalali}
                </p>
              </motion.div>
            </Link>
          </div>
        ))}
      </Slider>
      
      <div className="mt-3 text-center">
        <Link to="/businesses" className="text-blue-500 text-sm mr-4">
          همه کسب‌وکارها
        </Link>
        <Link to="/businesses/create" className="text-green-500 text-sm">
          افزودن کسب‌وکار
        </Link>
      </div>
    </motion.div>
  );
};

export default BusinessWidget; 