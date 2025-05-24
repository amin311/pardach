import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChevronRight, FaChevronLeft, FaEye } from 'react-icons/fa';

const PromotionalSlider = ({ items }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(1); // 1 = راست به چپ، -1 = چپ به راست

  // تابع برای رفتن به اسلاید بعدی
  const nextSlide = () => {
    setDirection(1);
    setCurrentIndex((prevIndex) => (prevIndex + 1) % items.length);
  };

  // تابع برای رفتن به اسلاید قبلی
  const prevSlide = () => {
    setDirection(-1);
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? items.length - 1 : prevIndex - 1
    );
  };

  // انیمیشن‌ها برای اسلایدها
  const slideVariants = {
    enter: (direction) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction) => ({
      x: direction > 0 ? -1000 : 1000,
      opacity: 0
    })
  };

  // افکت ترانزیشن
  const transition = {
    type: "tween",
    duration: 0.5
  };

  return (
    <div className="relative rounded-xl overflow-hidden shadow-md h-[300px] bg-gray-100">
      {/* فلش‌های ناوبری */}
      <button
        onClick={prevSlide}
        className="absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-white/70 hover:bg-white p-2 rounded-full shadow-md transition-colors"
        aria-label="اسلاید قبلی"
      >
        <FaChevronLeft className="text-blue-600" />
      </button>
      
      <button
        onClick={nextSlide}
        className="absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-white/70 hover:bg-white p-2 rounded-full shadow-md transition-colors"
        aria-label="اسلاید بعدی"
      >
        <FaChevronRight className="text-blue-600" />
      </button>
      
      {/* انیمیشن اسلایدها */}
      <AnimatePresence initial={false} custom={direction}>
        <motion.div
          key={currentIndex}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={transition}
          className="absolute inset-0"
        >
          <Link to={items[currentIndex].link} className="block h-full">
            <div className="relative h-full">
              {/* تصویر پس‌زمینه */}
              <img
                src={items[currentIndex].image_url}
                alt={items[currentIndex].title}
                className="w-full h-full object-cover"
              />
              
              {/* لایه تیره روی تصویر */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
              
              {/* محتوای متنی */}
              <div className="absolute bottom-0 right-0 left-0 p-6 text-white">
                <h3 className="text-2xl font-bold mb-2">{items[currentIndex].title}</h3>
                <p className="mb-4 text-white/90 max-w-2xl">{items[currentIndex].description}</p>
                <div className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 transition-colors px-4 py-2 rounded-md">
                  <FaEye />
                  <span>مشاهده بیشتر</span>
                </div>
              </div>
            </div>
          </Link>
        </motion.div>
      </AnimatePresence>
      
      {/* نشانگر اسلایدها */}
      <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2 z-10">
        {items.map((_, index) => (
          <button
            key={index}
            onClick={() => {
              setDirection(index > currentIndex ? 1 : -1);
              setCurrentIndex(index);
            }}
            className={`w-3 h-3 rounded-full transition-colors ${
              index === currentIndex ? 'bg-white' : 'bg-white/50 hover:bg-white/70'
            }`}
            aria-label={`رفتن به اسلاید ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default PromotionalSlider;