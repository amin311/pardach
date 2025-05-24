import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FaPaintBrush, FaLayerGroup, FaShoppingCart, 
  FaCreditCard, FaComments, FaBell, FaChartBar, 
  FaBriefcase, FaTachometerAlt, FaUsers, FaCog
} from 'react-icons/fa';

/**
 * کامپوننت منوی ناوبری اصلی با آیکون‌های بزرگ و رنگی
 * @param {Array} menuItems - آیتم‌های منو
 * @param {String} userRole - نقش کاربر (admin یا user)
 */
const NavigationMenuWidget = ({ menuItems, userRole }) => {
  // نگاشت آیکون‌ها به نام‌های آیکون
  const iconMap = {
    'fa-paint-brush': <FaPaintBrush size={24} />,
    'fa-layer-group': <FaLayerGroup size={24} />,
    'fa-shopping-cart': <FaShoppingCart size={24} />,
    'fa-credit-card': <FaCreditCard size={24} />,
    'fa-comments': <FaComments size={24} />,
    'fa-bell': <FaBell size={24} />,
    'fa-chart-bar': <FaChartBar size={24} />,
    'fa-briefcase': <FaBriefcase size={24} />,
    'fa-tachometer-alt': <FaTachometerAlt size={24} />,
    'fa-users': <FaUsers size={24} />,
    'fa-cog': <FaCog size={24} />
  };

  // رنگ‌های پس‌زمینه برای هر آیتم
  const bgColors = {
    'designs': 'from-pink-500 to-rose-500',
    'templates': 'from-purple-500 to-indigo-500',
    'orders': 'from-blue-500 to-cyan-500',
    'payments': 'from-emerald-500 to-green-500',
    'chats': 'from-amber-500 to-orange-500',
    'notifications': 'from-red-500 to-pink-500',
    'reports': 'from-violet-500 to-purple-500',
    'businesses': 'from-indigo-500 to-blue-500',
    'dashboard': 'from-slate-700 to-slate-900',
    'users': 'from-cyan-500 to-teal-500',
    'settings': 'from-gray-600 to-gray-800'
  };

  // استخراج کلید از لینک (مثلاً "/designs" به "designs")
  const getLinkKey = (link) => {
    const path = link.split('/')[1];
    return path || 'home';
  };

  // انیمیشن برای کارت‌های منو
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-gray-800">
        <span className="w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-600 rounded-md">
          <FaLayerGroup />
        </span>
        منوی دسترسی سریع
      </h2>

      <motion.div 
        className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {menuItems?.filter(item => item.visible).map((item, index) => {
          const linkKey = getLinkKey(item.link);
          const bgColor = bgColors[linkKey] || 'from-gray-500 to-gray-700';
          
          return (
            <motion.div key={index} variants={item}>
              <Link 
                to={item.link} 
                className="block h-full"
              >
                <motion.div 
                  className={`bg-gradient-to-br ${bgColor} text-white rounded-lg p-4 h-full flex flex-col items-center justify-center text-center shadow-sm hover:shadow-md transition-shadow`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="bg-white/20 p-3 rounded-full mb-3">
                    {iconMap[item.icon] || <FaCog size={24} />}
                  </div>
                  <h3 className="font-bold">{item.title}</h3>
                </motion.div>
              </Link>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
};

export default NavigationMenuWidget; 