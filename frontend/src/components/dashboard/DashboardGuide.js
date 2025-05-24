import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { FaLightbulb, FaArrowRight, FaTimes, FaChevronLeft, FaChevronRight } from 'react-icons/fa';

/**
 * کامپوننت راهنمای تعاملی داشبورد
 * راهنمای گام به گام برای کاربران کم‌سواد
 * @param {number} userId - شناسه کاربر
 * @param {boolean} hasSeenGuide - آیا کاربر قبلاً راهنما را دیده است
 */
const DashboardGuide = ({ userId, hasSeenGuide }) => {
  // وضعیت نمایش راهنما
  const [isVisible, setIsVisible] = useState(!hasSeenGuide);
  // گام فعلی راهنما
  const [currentStep, setCurrentStep] = useState(0);
  // وضعیت دکمه راهنما
  const [showGuideButton, setShowGuideButton] = useState(hasSeenGuide);
  // موقعیت المان هایلایت شده
  const [highlightPosition, setHighlightPosition] = useState({
    top: 0,
    left: 0,
    width: 0,
    height: 0
  });
  
  // رفرنس برای محتوای راهنما
  const guideRef = useRef(null);

  // مراحل راهنما با عنوان و متن و سلکتور المان هدف
  const guideSteps = [
    {
      title: 'به داشبورد خوش آمدید',
      text: 'این صفحه خلاصه‌ای از وضعیت سفارش‌ها، پرداخت‌ها و اعلان‌های شما را نمایش می‌دهد. با این راهنما با بخش‌های مختلف آشنا می‌شوید.',
      target: '.dashboard-header'
    },
    {
      title: 'آمار کلی',
      text: 'این بخش آمار کلی شامل تعداد سفارش‌ها، مجموع فروش، تعداد پرداخت‌ها، اعلانات خوانده نشده و تعداد گزارش‌ها را نشان می‌دهد.',
      target: '.dashboard-stats'
    },
    {
      title: 'فیلتر زمانی',
      text: 'با استفاده از این فیلتر می‌توانید بازه زمانی مورد نظر خود را برای مشاهده اطلاعات انتخاب کنید (۷ روز، ۳۰ روز، یا ۹۰ روز اخیر).',
      target: '.dashboard-filters'
    },
    {
      title: 'نمودار سفارش‌ها',
      text: 'این نمودار میزان فروش روزانه شما را نمایش می‌دهد. ستون‌های بلندتر نشان‌دهنده فروش بیشتر در آن روز است.',
      target: '.orders-chart'
    },
    {
      title: 'نمودار پرداخت‌ها',
      text: 'این نمودار میزان پرداخت‌های دریافتی روزانه را نمایش می‌دهد. می‌توانید با حرکت نشانگر روی نمودار، جزئیات هر روز را مشاهده کنید.',
      target: '.payments-chart'
    },
    {
      title: 'تبریک!',
      text: 'شما با موفقیت با داشبورد آشنا شدید. اکنون می‌توانید به راحتی از امکانات آن استفاده کنید. در صورت نیاز به راهنمایی بیشتر، روی دکمه «راهنما» کلیک کنید.',
      target: '.dashboard-header'
    }
  ];

  // محاسبه موقعیت المان هدف
  useEffect(() => {
    if (isVisible && guideSteps.length > currentStep) {
      const targetElement = document.querySelector(guideSteps[currentStep].target);
      
      if (targetElement) {
        const rect = targetElement.getBoundingClientRect();
        setHighlightPosition({
          top: rect.top + window.scrollY,
          left: rect.left + window.scrollX,
          width: rect.width,
          height: rect.height
        });
        
        // اسکرول به موقعیت المان هدف
        window.scrollTo({
          top: rect.top + window.scrollY - 100,
          behavior: 'smooth'
        });
      }
    }
  }, [currentStep, isVisible]);

  // رفتن به مرحله بعدی راهنما
  const handleNext = () => {
    if (currentStep < guideSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleFinish();
    }
  };

  // رفتن به مرحله قبلی راهنما
  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // پایان راهنما و ذخیره وضعیت در بک‌اند
  const handleFinish = async () => {
    setIsVisible(false);
    setShowGuideButton(true);
    
    try {
      await axios.post('/api/main/settings/', 
        {
          key: `user_${userId}_dashboard_guide`,
          value: 'true'
        },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        }
      );
    } catch (error) {
      console.error('Error saving guide status:', error);
    }
  };

  // شروع مجدد راهنما
  const handleShowGuide = () => {
    setCurrentStep(0);
    setIsVisible(true);
    setShowGuideButton(false);
  };

  return (
    <>
      {/* دکمه نمایش راهنما */}
      <AnimatePresence>
        {showGuideButton && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="fixed bottom-8 left-8 z-50 bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-3 rounded-full shadow-lg flex items-center justify-center"
            onClick={handleShowGuide}
            title="نمایش راهنما"
          >
            <FaLightbulb size={24} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* راهنمای تعاملی */}
      <AnimatePresence>
        {isVisible && (
          <>
            {/* لایه پوشاننده کل صفحه */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black z-40"
              onClick={handleFinish}
            />
            
            {/* هایلایت المان موردنظر */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute z-40 pointer-events-none"
              style={{
                top: `${highlightPosition.top}px`,
                left: `${highlightPosition.left}px`,
                width: `${highlightPosition.width}px`,
                height: `${highlightPosition.height}px`,
                boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.7)'
              }}
            >
              <div className="absolute inset-0 border-4 border-blue-500 rounded-lg"></div>
            </motion.div>
            
            {/* محتوای راهنما */}
            <motion.div
              ref={guideRef}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
              className="fixed bottom-10 left-1/2 transform -translate-x-1/2 z-50 bg-white rounded-xl shadow-2xl p-6 max-w-md rtl"
              style={{ minWidth: '320px', maxWidth: '90%' }}
            >
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-xl font-bold text-blue-600">
                  {guideSteps[currentStep].title}
                </h3>
                <button
                  onClick={handleFinish}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <FaTimes size={20} />
                </button>
              </div>

              <div className="mb-2 text-gray-500 text-sm">
                گام {currentStep + 1} از {guideSteps.length}
              </div>
              
              <p className="text-gray-700 mb-6">
                {guideSteps[currentStep].text}
              </p>
              
              <div className="flex justify-between">
                <button
                  onClick={handlePrev}
                  className={`px-4 py-2 rounded-md ${
                    currentStep > 0 
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  } transition flex items-center gap-1`}
                  disabled={currentStep === 0}
                >
                  <FaChevronRight />
                  <span>قبلی</span>
                </button>
                
                <button
                  onClick={handleNext}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition flex items-center gap-1"
                >
                  <span>{currentStep < guideSteps.length - 1 ? 'بعدی' : 'پایان'}</span>
                  {currentStep < guideSteps.length - 1 ? <FaChevronLeft /> : <FaArrowRight />}
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default DashboardGuide; 