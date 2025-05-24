import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaPlus, FaEdit, FaEye } from 'react-icons/fa';

// کامپوننت کارت قالب برای نمایش هر قالب
const TemplateCard = ({ template }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      className="bg-white rounded-lg shadow-md overflow-hidden"
    >
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800">{template.title}</h3>
        <p className="text-gray-600 mt-2 text-sm line-clamp-2">{template.description}</p>
        <div className="mt-4 flex justify-between items-center">
          <span className="text-blue-600 font-semibold">
            {template.base_price.toLocaleString()} تومان
          </span>
          <div className="flex space-x-2 rtl:space-x-reverse">
            <Link
              to={`/templates/${template.id}`}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
              title="مشاهده جزئیات"
            >
              <FaEye />
            </Link>
            <Link
              to={`/templates/use/${template.id}`}
              className="p-2 text-green-600 hover:bg-green-50 rounded-full"
              title="استفاده از قالب"
            >
              <FaPlus />
            </Link>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const ListTemplates = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/templates/templates/');
      // فقط قالب‌های منتشر شده را نمایش می‌دهیم
      const publishedTemplates = response.data.filter(
        (template) => template.status === 'PUBLISHED'
      );
      setTemplates(publishedTemplates);
      setLoading(false);
    } catch (error) {
      toast.error('خطا در دریافت قالب‌ها');
      setLoading(false);
      console.error('Error fetching templates:', error);
    }
  };

  // فیلتر کردن قالب‌ها براساس متن جستجو
  const filteredTemplates = templates.filter((template) =>
    template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">قالب‌های موجود</h1>
      </div>

      {/* بخش جستجو */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="جستجو در قالب‌ها..."
            className="w-full p-3 pl-10 pr-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              ></path>
            </svg>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-gray-500 text-lg">هیچ قالبی یافت نشد!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <TemplateCard key={template.id} template={template} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ListTemplates; 