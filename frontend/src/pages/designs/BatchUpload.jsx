import React, { useState, useEffect } from 'react';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Select from 'react-select';

const BatchUpload = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previewFiles, setPreviewFiles] = useState([]);
  const [formData, setFormData] = useState({
    categories: [],
    tags: [],
    families: [],
    type: '',
    status: 'draft',
    is_public: true
  });
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [families, setFamilies] = useState([]);

  // بارگذاری دسته‌بندی‌ها، برچسب‌ها و خانواده‌ها در ابتدای لود صفحه
  useEffect(() => {
    const fetchData = async () => {
      try {
        const headers = { Authorization: `Bearer ${localStorage.getItem('access_token')}` };
        
        const [categoriesRes, tagsRes, familiesRes] = await Promise.all([
          axiosInstance.get('/api/designs/categories/', { headers }),
          axiosInstance.get('/api/designs/tags/', { headers }),
          axiosInstance.get('/api/designs/families/', { headers })
        ]);
        
        setCategories(categoriesRes.data.map(cat => ({ value: cat.id, label: cat.full_path || cat.name })));
        setTags(tagsRes.data.map(tag => ({ value: tag.id, label: tag.name })));
        setFamilies(familiesRes.data.map(fam => ({ value: fam.id, label: fam.name })));
      } catch (error) {
        toast.error('خطا در بارگذاری اطلاعات پایه');
        console.error(error);
      }
    };
    
    fetchData();
  }, []);

  // انتخاب فایل‌ها
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length === 0) return;
    
    // بررسی فرمت‌های مجاز (فقط تصاویر و SVG)
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'];
    const validFiles = files.filter(file => allowedTypes.includes(file.type));
    
    if (validFiles.length !== files.length) {
      toast.warning('برخی فایل‌ها با فرمت غیرمجاز انتخاب شده و حذف شدند');
    }
    
    setSelectedFiles(validFiles);
    
    // ایجاد پیش‌نمایش برای فایل‌ها
    const previews = validFiles.map(file => ({
      name: file.name,
      size: (file.size / 1024).toFixed(1) + ' کیلوبایت',
      url: URL.createObjectURL(file)
    }));
    
    setPreviewFiles(previews);
  };

  // تغییر مقادیر فرم
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFormData({
        ...formData,
        [name]: checked
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  // حذف یک فایل از لیست
  const removeFile = (index) => {
    const newFiles = [...selectedFiles];
    const newPreviews = [...previewFiles];
    
    // آزادسازی URL برای جلوگیری از نشت حافظه
    URL.revokeObjectURL(newPreviews[index].url);
    
    newFiles.splice(index, 1);
    newPreviews.splice(index, 1);
    
    setSelectedFiles(newFiles);
    setPreviewFiles(newPreviews);
  };

  // ارسال فرم آپلود دسته‌ای
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (selectedFiles.length === 0) {
      toast.warning('لطفاً حداقل یک فایل انتخاب کنید');
      return;
    }
    
    if (!formData.type) {
      toast.warning('نوع طرح الزامی است');
      return;
    }
    
    setLoading(true);
    setUploadProgress(0);
    
    try {
      const form = new FormData();
      
      // افزودن فایل‌ها به فرم
      selectedFiles.forEach(file => {
        form.append('design_files', file);
      });
      
      // افزودن سایر فیلدها
      form.append('type', formData.type);
      form.append('status', formData.status);
      form.append('is_public', formData.is_public);
      
      // افزودن رابطه‌های چندتایی
      formData.categories.forEach(id => form.append('categories', id));
      formData.tags.forEach(id => form.append('tags', id));
      formData.families.forEach(id => form.append('families', id));
      
      const response = await axiosInstance.post('/api/designs/batch-upload/', form, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      toast.success(`${response.data.length} طرح با موفقیت آپلود شد`);
      navigate('/designs');
    } catch (error) {
      toast.error('خطا در آپلود طرح‌ها');
      console.error(error);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-5xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-lg shadow-md"
      >
        <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <span className="text-blue-500">📤</span>
          آپلود دسته‌ای طرح‌ها
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* بخش انتخاب فایل */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              id="files"
              onChange={handleFileSelect}
              multiple
              accept="image/*,.svg"
              className="hidden"
            />
            
            <label htmlFor="files" className="cursor-pointer block">
              <div className="flex flex-col items-center">
                <span className="text-4xl mb-2">📁</span>
                <span className="text-lg font-medium">فایل‌ها را انتخاب کنید یا بکشید و رها کنید</span>
                <span className="text-sm text-gray-500 mt-1">فرمت‌های مجاز: JPG، PNG، GIF، SVG</span>
              </div>
            </label>
          </div>
          
          {/* پیش‌نمایش فایل‌های انتخاب شده */}
          {previewFiles.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">
                {selectedFiles.length} فایل انتخاب شده
              </h3>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {previewFiles.map((file, index) => (
                  <div key={index} className="relative border rounded-md overflow-hidden bg-gray-50">
                    <div className="h-32 flex items-center justify-center">
                      <img src={file.url} alt={file.name} className="max-h-full max-w-full" />
                    </div>
                    <div className="p-2 text-xs truncate">{file.name}</div>
                    <div className="p-2 text-xs text-gray-500">{file.size}</div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ستون اول - تنظیمات پایه */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">نوع طرح *</label>
                <input
                  type="text"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  placeholder="مثلاً: گرافیکی، وکتور"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">این نوع به تمام طرح‌های آپلود شده اعمال می‌شود</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="draft">پیش‌نویس</option>
                  <option value="published">منتشر شده</option>
                  <option value="archived">بایگانی شده</option>
                </select>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="mr-2 block text-sm text-gray-700">
                  نمایش عمومی (برای همه کاربران قابل مشاهده باشد)
                </label>
              </div>
            </div>
            
            {/* ستون دوم - روابط */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">دسته‌بندی‌ها</label>
                <Select
                  isMulti
                  name="categories"
                  options={categories}
                  value={categories.filter(cat => formData.categories.includes(cat.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    categories: selected ? selected.map(option => option.value) : []
                  })}
                  placeholder="دسته‌بندی‌ها را انتخاب کنید"
                  noOptionsMessage={() => "موردی یافت نشد"}
                  className="text-sm"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">برچسب‌ها</label>
                <Select
                  isMulti
                  name="tags"
                  options={tags}
                  value={tags.filter(tag => formData.tags.includes(tag.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    tags: selected ? selected.map(option => option.value) : []
                  })}
                  placeholder="برچسب‌ها را انتخاب کنید"
                  noOptionsMessage={() => "موردی یافت نشد"}
                  className="text-sm"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">خانواده‌ها</label>
                <Select
                  isMulti
                  name="families"
                  options={families}
                  value={families.filter(fam => formData.families.includes(fam.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    families: selected ? selected.map(option => option.value) : []
                  })}
                  placeholder="خانواده‌ها را انتخاب کنید"
                  noOptionsMessage={() => "موردی یافت نشد"}
                  className="text-sm"
                />
              </div>
            </div>
          </div>
          
          {/* نوار پیشرفت */}
          {loading && uploadProgress > 0 && (
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full transition-all" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <div className="text-center mt-2 text-sm">
                {uploadProgress}% آپلود شده
              </div>
            </div>
          )}
          
          <div className="flex justify-between pt-4 border-t">
            <Link
              to="/designs"
              className="py-2 px-4 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
            >
              انصراف
            </Link>
            
            <button
              type="submit"
              disabled={loading || selectedFiles.length === 0}
              className={`py-2 px-6 rounded-md text-white flex items-center gap-2 
                ${loading || selectedFiles.length === 0 ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} 
                transition`}
            >
              {loading ? (
                <>
                  <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  در حال آپلود...
                </>
              ) : (
                <>
                  <span>📤</span>
                  آپلود {selectedFiles.length} طرح
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default BatchUpload; 