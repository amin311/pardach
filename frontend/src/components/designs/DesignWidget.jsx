import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import Slider from "react-slick";
import { motion } from 'framer-motion';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const DesignWidget = () => {
  const [designs, setDesigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDesigns();
  }, []);

  const fetchDesigns = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/designs/designs/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      // نمایش فقط 5 طرح آخر
      setDesigns(response.data.slice(0, 5));
    } catch (error) {
      toast.error('خطا در بارگذاری طرح‌ها');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    rtl: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        }
      }
    ]
  };

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  if (designs.length === 0) {
    return null;
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="p-4 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span className="text-blue-500">🎨</span>
          طرح‌های اخیر
        </h2>
        <Link to="/designs" className="text-blue-500 text-sm hover:underline">
          مشاهده همه طرح‌ها
        </Link>
      </div>

      <div className="p-2">
        <Slider {...settings}>
          {designs.map(design => (
            <div key={design.id} className="px-2">
              <Link to={`/designs/${design.id}`}>
                <motion.div 
                  whileHover={{ y: -5 }}
                  className="bg-white p-3 rounded-lg shadow-md h-64 flex flex-col"
                >
                  <div className="h-40 overflow-hidden rounded-md mb-2">
                    {design.product_image ? (
                      <img 
                        src={design.product_image} 
                        alt={design.title} 
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400">
                        بدون تصویر
                      </div>
                    )}
                  </div>
                  <h3 className="text-sm font-bold truncate">{design.title}</h3>
                  <p className="text-xs text-gray-600 mt-1">
                    {design.categories.length > 0 
                      ? design.categories.map(cat => cat.name).join('، ') 
                      : 'بدون دسته‌بندی'}
                  </p>
                  <div className="mt-auto pt-2 flex justify-between items-center text-xs text-gray-500">
                    <span>تاریخ: {design.created_at}</span>
                    <span>بازدید: {design.view_count}</span>
                  </div>
                </motion.div>
              </Link>
            </div>
          ))}
        </Slider>
      </div>
    </motion.div>
  );
};

export default DesignWidget; 