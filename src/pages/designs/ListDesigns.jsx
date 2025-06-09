import React, { useState, useEffect } from 'react';
import axiosInstance from '../../lib/axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Select from 'react-select';

const ListDesigns = ({ userId, isAdmin }) => {
  const [designs, setDesigns] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState({ category: '', tag: '', search: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.tag) params.append('tag', filters.tag);
    if (filters.search) params.append('search', filters.search);

    setLoading(true);
    
    axiosInstance.get(`/api/designs/designs/?${params.toString()}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => setDesigns(res.data))
      .catch(() => toast.error('خطا در بارگذاری طرح‌ها'))
      .finally(() => setLoading(false));

    axiosInstance.get('/api/designs/categories/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => setCategories(res.data.map(cat => ({ value: cat.id, label: cat.full_path }))))
      .catch(() => toast.error('خطا در بارگذاری دسته‌بندی‌ها'));

    axiosInstance.get('/api/designs/tags/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => setTags(res.data.map(tag => ({ value: tag.id, label: tag.name }))))
      .catch(() => toast.error('خطا در بارگذاری برچسب‌ها'));
  }, [filters]);

  const handleDelete = async (designId) => {
    if (window.confirm('آیا از حذف طرح مطمئن هستید؟')) {
      try {
        await axiosInstance.delete(`/api/designs/designs/${designId}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setDesigns(designs.filter(design => design.id !== designId));
        toast.success('طرح حذف شد');
      } catch (error) {
        toast.error('خطا در حذف طرح');
      }
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <motion.h2 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2"
      >
        <span className="text-3xl">🎨</span>
        مدیریت طرح‌ها
      </motion.h2>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6 flex flex-wrap gap-4 justify-between items-center"
      >
        {/* جستجو و فیلتر */}
        <div className="flex flex-wrap gap-4 flex-1 items-center">
          <Select
            options={categories}
            value={categories.find(cat => cat.value === filters.category)}
            onChange={option => setFilters({ ...filters, category: option?.value || '' })}
            placeholder="دسته‌بندی..."
            className="w-full md:w-40 text-sm"
            isClearable
          />
          <Select
            options={tags}
            value={tags.find(tag => tag.value === filters.tag)}
            onChange={option => setFilters({ ...filters, tag: option?.value || '' })}
            placeholder="برچسب..."
            className="w-full md:w-40 text-sm"
            isClearable
          />
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            placeholder="جستجو در طرح‌ها..."
            className="p-2 border rounded flex-1 min-w-[200px] text-sm"
          />
        </div>
        
        {/* دکمه‌های اقدام */}
        <div className="flex gap-2">
          <Link
            to="/designs/create"
            className="bg-green-500 text-white p-2 rounded flex items-center gap-2 hover:bg-green-600 transition duration-200"
          >
            <span>➕</span>
            افزودن طرح
          </Link>
          <Link
            to="/designs/batch-upload"
            className="bg-blue-500 text-white p-2 rounded flex items-center gap-2 hover:bg-blue-600 transition duration-200"
          >
            <span>📤</span>
            آپلود دسته‌ای
          </Link>
        </div>
      </motion.div>
      
      {/* نمایش لودینگ */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {/* بدون طرح */}
      {!loading && designs.length === 0 && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center py-12 bg-gray-50 rounded-lg"
        >
          <div className="text-6xl mb-4">🖼️</div>
          <p className="text-gray-500">هیچ طرحی یافت نشد</p>
          <p className="text-sm text-gray-400 mt-2">برای شروع، یک طرح جدید اضافه کنید</p>
        </motion.div>
      )}
      
      {/* نمایش طرح‌ها */}
      {!loading && designs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {designs.map((design, index) => (
            <motion.div
              key={design.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-lg shadow-md overflow-hidden"
            >
              <div className="h-48 overflow-hidden bg-gray-100">
                {design.product_image ? (
                  <img 
                    src={design.product_image} 
                    alt={design.title} 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    بدون تصویر
                  </div>
                )}
              </div>
              
              <div className="p-4">
                <div className="mb-2">
                  <h3 className="font-bold text-lg truncate">{design.title}</h3>
                  <p className="text-sm text-gray-600 truncate">
                    {design.categories.length > 0 
                      ? design.categories.map(cat => cat.name).join('، ') 
                      : 'بدون دسته‌بندی'}
                  </p>
                </div>
                
                <div className="flex flex-wrap gap-1 mb-3">
                  {design.tags.slice(0, 3).map(tag => (
                    <span key={tag.id} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {tag.name}
                    </span>
                  ))}
                  {design.tags.length > 3 && (
                    <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                      +{design.tags.length - 3}
                    </span>
                  )}
                </div>
                
                <div className="flex justify-between text-xs text-gray-500 mb-3">
                  <span>نوع: {design.type}</span>
                  <span>وضعیت: {design.status}</span>
                </div>
                
                <div className="flex justify-between text-xs text-gray-500 mb-3">
                  <span>بازدید: {design.view_count}</span>
                  <span>دانلود: {design.download_count}</span>
                  <span>تاریخ: {design.created_at}</span>
                </div>
                
                <div className="flex gap-2 mt-2">
                  <Link 
                    to={`/designs/${design.id}`} 
                    className="flex-1 py-1.5 px-2 text-center text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                  >
                    مشاهده
                  </Link>
                  
                  {(design.created_by === userId || isAdmin) && (
                    <>
                      <Link 
                        to={`/designs/edit/${design.id}`} 
                        className="flex-1 py-1.5 px-2 text-center text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition"
                      >
                        ویرایش
                      </Link>
                      <button
                        onClick={() => handleDelete(design.id)}
                        className="flex-1 py-1.5 px-2 text-center text-sm bg-red-500 text-white rounded hover:bg-red-600 transition"
                      >
                        حذف
                      </button>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ListDesigns; 