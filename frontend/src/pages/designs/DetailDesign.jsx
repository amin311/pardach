import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const DetailDesign = ({ userId, isAdmin }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [design, setDesign] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDesign();
  }, [id]);

  const fetchDesign = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(`/api/designs/designs/${id}/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setDesign(response.data);
    } catch (error) {
      toast.error('خطا در بارگذاری اطلاعات طرح');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('آیا از حذف این طرح اطمینان دارید؟')) {
      try {
        await axiosInstance.delete(`/api/designs/designs/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        toast.success('طرح با موفقیت حذف شد');
        navigate('/designs');
      } catch (error) {
        toast.error('خطا در حذف طرح');
        console.error(error);
      }
    }
  };

  const handleDownload = async () => {
    try {
      if (design.svg_file) {
        // افزایش شمارنده دانلود
        await axiosInstance.put(`/api/designs/designs/${id}/`, 
          { download_count: design.download_count + 1 },
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        
        // شبیه‌سازی دانلود - در نسخه واقعی باید به URL فایل هدایت شود
        window.open(design.svg_file, '_blank');
        toast.success('دانلود فایل آغاز شد');
      } else {
        toast.warning('فایل SVG برای این طرح موجود نیست');
      }
    } catch (error) {
      toast.error('خطا در دانلود فایل');
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!design) {
    return (
      <div className="text-center p-8">
        <div className="text-6xl mb-4">🔍</div>
        <h2 className="text-2xl font-bold mb-2">طرح یافت نشد</h2>
        <p className="text-gray-600 mb-4">طرح مورد نظر شما موجود نیست یا حذف شده است.</p>
        <Link to="/designs" className="text-blue-500 hover:underline">
          بازگشت به لیست طرح‌ها
        </Link>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="container mx-auto p-4 max-w-5xl"
    >
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {/* نوار بالایی با عنوان و دکمه‌های اقدام */}
        <div className="bg-gray-50 p-4 border-b flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <span className="text-blue-500">🎨</span>
            {design.title}
          </h1>
          
          <div className="flex gap-2">
            <Link 
              to="/designs" 
              className="py-2 px-4 text-sm text-gray-600 border rounded-md hover:bg-gray-50 transition"
            >
              بازگشت به لیست
            </Link>
            
            {design.svg_file && (
              <button
                onClick={handleDownload}
                className="py-2 px-4 text-sm bg-green-500 text-white rounded-md hover:bg-green-600 transition flex items-center gap-1"
              >
                <span>📥</span> دانلود فایل
              </button>
            )}
            
            {(isAdmin || design.created_by === userId || (design.user && design.user.id === userId)) && (
              <>
                <Link 
                  to={`/designs/edit/${design.id}`} 
                  className="py-2 px-4 text-sm bg-yellow-500 text-white rounded-md hover:bg-yellow-600 transition flex items-center gap-1"
                >
                  <span>✏️</span> ویرایش
                </Link>
                <button
                  onClick={handleDelete}
                  className="py-2 px-4 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition flex items-center gap-1"
                >
                  <span>🗑️</span> حذف
                </button>
              </>
            )}
          </div>
        </div>
        
        <div className="p-6">
          {/* بخش تصویر و اطلاعات کلی */}
          <div className="flex flex-col md:flex-row gap-8 mb-8">
            {/* تصویر طرح */}
            <div className="w-full md:w-1/2">
              <div className="bg-gray-100 rounded-lg overflow-hidden h-80 flex items-center justify-center">
                {design.product_image ? (
                  <img 
                    src={design.product_image} 
                    alt={design.title} 
                    className="max-w-full max-h-full object-contain"
                  />
                ) : (
                  <div className="text-gray-400 text-lg">
                    تصویر محصول موجود نیست
                  </div>
                )}
              </div>
              
              {/* آمار طرح */}
              <div className="flex justify-between mt-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <span>👁️</span>
                  <span>بازدید: {design.view_count}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>📥</span>
                  <span>دانلود: {design.download_count}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>📅</span>
                  <span>تاریخ: {design.created_at}</span>
                </div>
              </div>
            </div>
            
            {/* اطلاعات طرح */}
            <div className="w-full md:w-1/2">
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <h3 className="text-lg font-bold mb-2">توضیحات</h3>
                  <p className="text-gray-700">{design.description || 'بدون توضیحات'}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-bold mb-1">نوع</h3>
                    <p className="text-gray-700">{design.type}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold mb-1">سایز</h3>
                    <p className="text-gray-700">{design.size || 'نامشخص'}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold mb-1">ابعاد</h3>
                    <p className="text-gray-700">{design.width && design.height ? `${design.width}×${design.height}` : 'نامشخص'}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold mb-1">وضعیت</h3>
                    <p className="text-gray-700">{design.status}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold mb-1">نسبت تصویر</h3>
                    <p className="text-gray-700">{design.aspect_ratio || 'نامشخص'}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold mb-1">سازنده</h3>
                    <p className="text-gray-700">{design.created_by}</p>
                  </div>
                </div>
                
                {/* دسته‌بندی‌ها */}
                <div>
                  <h3 className="text-sm font-bold mb-1">دسته‌بندی‌ها</h3>
                  {design.categories.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {design.categories.map(category => (
                        <span key={category.id} className="bg-gray-200 text-gray-800 rounded px-2 py-1 text-xs">
                          {category.name}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">بدون دسته‌بندی</p>
                  )}
                </div>
                
                {/* برچسب‌ها */}
                <div>
                  <h3 className="text-sm font-bold mb-1">برچسب‌ها</h3>
                  {design.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {design.tags.map(tag => (
                        <span key={tag.id} className="bg-blue-100 text-blue-800 rounded px-2 py-1 text-xs">
                          {tag.name}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">بدون برچسب</p>
                  )}
                </div>
                
                {/* خانواده‌ها */}
                <div>
                  <h3 className="text-sm font-bold mb-1">خانواده‌ها</h3>
                  {design.families.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {design.families.map(family => (
                        <span key={family.id} className="bg-green-100 text-green-800 rounded px-2 py-1 text-xs">
                          {family.name}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">بدون خانواده</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DetailDesign; 