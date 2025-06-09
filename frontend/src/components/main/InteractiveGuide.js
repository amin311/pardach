import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axiosInstance from './lib/axios';

/**
 * کامپوننت راهنمای تعاملی برای کاربران کم‌تجربه
 * این کامپوننت به کاربران جدید کمک می‌کند تا با قسمت‌های مختلف سیستم آشنا شوند
 * @param {Object} props - پراپرتی‌های کامپوننت
 * @param {number} props.userId - شناسه کاربر
 * @param {boolean} props.hasSeenGuide - آیا کاربر قبلاً راهنما را دیده است
 */
const InteractiveGuide = ({ userId, hasSeenGuide }) => {
  // وضعیت نمایش راهنما
  const [isVisible, setIsVisible] = useState(!hasSeenGuide);
  // گام فعلی راهنما
  const [currentStep, setCurrentStep] = useState(0);
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
      title: 'به سیستم مدیریت سفارش خوش آمدید',
      text: 'این راهنما به شما کمک می‌کند تا با بخش‌های مختلف سیستم آشنا شوید. می‌توانید در هر زمان با کلیک روی دکمه «پایان راهنما»، آن را متوقف کنید.',
      target: '.welcome-section'
    },
    {
      title: 'منوی ناوبری',
      text: 'از طریق این منو می‌توانید به بخش‌های مختلف سیستم دسترسی پیدا کنید. با کلیک روی هر آیکون، به صفحه مربوطه منتقل می‌شوید.',
      target: '.nav-menu-widget'
    },
    {
      title: 'داشبورد',
      text: 'در این قسمت خلاصه‌ای از وضعیت شما را مشاهده می‌کنید. تعداد سفارش‌ها، پرداخت‌ها و اعلان‌های جدید در اینجا نمایش داده می‌شود.',
      target: '.dashboard-widget'
    },
    {
      title: 'سفارش‌های اخیر',
      text: 'لیست آخرین سفارش‌های شما در این قسمت نمایش داده می‌شود. می‌توانید وضعیت هر سفارش را مشاهده کنید.',
      target: '.orders-widget'
    },
    {
      title: 'اعلان‌ها',
      text: 'در این بخش اعلان‌های سیستم نمایش داده می‌شود. حتماً اعلان‌های جدید را بررسی کنید تا از آخرین تغییرات و وضعیت سفارش‌های خود مطلع شوید.',
      target: '.notification-widget'
    },
    {
      title: 'تبریک!',
      text: 'شما با موفقیت با قسمت‌های اصلی سیستم آشنا شدید. اکنون می‌توانید به استفاده از سیستم بپردازید. در صورت نیاز به راهنمایی بیشتر، با پشتیبانی تماس بگیرید.',
      target: '.welcome-section'
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

  // پایان راهنما و ذخیره وضعیت در بک‌اند
  const handleFinish = async () => {
    setIsVisible(false);
    
    try {
      await axiosInstance.post('/api/main/settings/', 
        {
          key: `user_${userId}_has_seen_guide`,
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

  // اگر راهنما نمایش داده نشود، چیزی رندر نمی‌شود
  if (!isVisible) return null;

  return (
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
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-blue-600">
                {guideSteps[currentStep].title}
              </h3>
              <span className="text-gray-500 text-sm">
                {currentStep + 1}/{guideSteps.length}
              </span>
            </div>
            
            <p className="text-gray-700 mb-6">
              {guideSteps[currentStep].text}
            </p>
            
            <div className="flex justify-between">
              <button
                onClick={handleFinish}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
              >
                پایان راهنما
              </button>
              
              <button
                onClick={handleNext}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
              >
                {currentStep < guideSteps.length - 1 ? 'بعدی' : 'پایان'}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default InteractiveGuide; 