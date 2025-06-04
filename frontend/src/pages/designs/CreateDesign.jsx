import React, { useState, useEffect } from 'react';
import axios from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Select from 'react-select';

const CreateDesign = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    size: '',
    type: '',
    product_image: null,
    svg_file: null,
    category_ids: [],
    tag_ids: [],
    family_ids: [],
    status: 'draft',
    is_public: true
  });
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [families, setFamilies] = useState([]);
  const [preview, setPreview] = useState(null);

  // بارگذاری دسته‌بندی‌ها، برچسب‌ها و خانواده‌ها در ابتدای لود صفحه
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes, tagsRes, familiesRes] = await Promise.all([
          axios.get('/api/designs/categories/'),
          axios.get('/api/designs/tags/'),
          axios.get('/api/designs/families/')
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

  // تغییر مقادیر فرم
  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'file') {
      // برای فایل‌ها
      setFormData({
        ...formData,
        [name]: files[0]
      });
      
      // ایجاد پیش‌نمایش برای تصویر محصول
      if (name === 'product_image' && files[0]) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreview(reader.result);
        };
        reader.readAsDataURL(files[0]);
      }
    } else if (type === 'checkbox') {
      // برای چک‌باکس‌ها
      setFormData({
        ...formData,
        [name]: checked
      });
    } else {
      // برای ورودی‌های معمولی
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  // ارسال فرم
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.type) {
      toast.warning('عنوان و نوع طرح الزامی هستند');
      return;
    }
    
    setLoading(true);
    
    try {
      const form = new FormData();
      form.append('title', formData.title);
      form.append('description', formData.description || '');
      form.append('size', formData.size || '');
      form.append('type', formData.type);
      form.append('status', formData.status);
      form.append('is_public', formData.is_public);
      
      if (formData.product_image) form.append('product_image', formData.product_image);
      if (formData.svg_file) form.append('svg_file', formData.svg_file);
      
      // اضافه کردن رابطه‌های چندتایی
      formData.category_ids.forEach(id => form.append('category_ids', id));
      formData.tag_ids.forEach(id => form.append('tag_ids', id));
      formData.family_ids.forEach(id => form.append('family_ids', id));
      
      const response = await axios.post('/api/designs/designs/', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast.success('طرح با موفقیت ایجاد شد');
      navigate(`/designs/${response.data.id}`);
    } catch (error) {
      toast.error('خطا در ثبت طرح');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-lg shadow-md"
      >
        <h1 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <span className="text-blue-500">➕</span>
          افزودن طرح جدید
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ستون اول - اطلاعات پایه */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان طرح *</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  placeholder="عنوان طرح را وارد کنید"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">توضیحات</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  placeholder="توضیحاتی درباره طرح بنویسید"
                  rows="4"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
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
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">سایز</label>
                  <input
                    type="text"
                    name="size"
                    value={formData.size}
                    onChange={handleChange}
                    className="w-full p-2 border border-gray-300 rounded-md text-sm"
                    placeholder="مثلاً: 100x100"
                  />
                </div>
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
            
            {/* ستون دوم - فایل‌ها و روابط */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">تصویر محصول</label>
                <input
                  type="file"
                  name="product_image"
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  accept="image/*"
                />
                {preview && (
                  <div className="mt-2 relative h-32 w-full overflow-hidden rounded border border-gray-200">
                    <img src={preview} alt="پیش‌نمایش" className="h-full w-full object-contain" />
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">فایل SVG</label>
                <input
                  type="file"
                  name="svg_file"
                  onChange={handleChange}
                  className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  accept=".svg"
                />
                <p className="text-xs text-gray-500 mt-1">فقط فایل‌های با فرمت SVG مجاز هستند</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">دسته‌بندی‌ها</label>
                <Select
                  isMulti
                  name="categories"
                  options={categories}
                  value={categories.filter(cat => formData.category_ids.includes(cat.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    category_ids: selected ? selected.map(option => option.value) : []
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
                  value={tags.filter(tag => formData.tag_ids.includes(tag.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    tag_ids: selected ? selected.map(option => option.value) : []
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
                  value={families.filter(fam => formData.family_ids.includes(fam.value))}
                  onChange={(selected) => setFormData({
                    ...formData,
                    family_ids: selected ? selected.map(option => option.value) : []
                  })}
                  placeholder="خانواده‌ها را انتخاب کنید"
                  noOptionsMessage={() => "موردی یافت نشد"}
                  className="text-sm"
                />
              </div>
            </div>
          </div>
          
          <div className="flex justify-between pt-4 border-t">
            <Link
              to="/designs"
              className="py-2 px-4 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
            >
              انصراف
            </Link>
            
            <button
              type="submit"
              disabled={loading}
              className={`py-2 px-6 rounded-md text-white flex items-center gap-2 ${loading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'} transition`}
            >
              {loading ? (
                <>
                  <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  در حال ثبت...
                </>
              ) : (
                <>
                  <span>💾</span>
                  ذخیره طرح
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default CreateDesign; 