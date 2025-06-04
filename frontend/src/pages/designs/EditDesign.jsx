import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';
import Select from 'react-select';

const EditDesign = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    size: '',
    type: '',
    status: 'draft',
    is_public: false,
    category_ids: [],
    tag_ids: [],
    family_ids: [],
    product_image: null,
    svg_file: null
  });
  
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [families, setFamilies] = useState([]);
  const [imagePreview, setImagePreview] = useState(null);
  const [svgPreview, setSvgPreview] = useState(null);
  
  // فرمت آپشن‌ها برای سلکت‌ها
  const formatOptions = (items) => {
    return items.map(item => ({
      value: item.id,
      label: item.name || item.title
    }));
  };
  
  // فرمت آپشن‌های فعلی
  const formatCurrentOptions = (ids, options) => {
    return ids.map(id => options.find(opt => opt.value === id)).filter(Boolean);
  };

  useEffect(() => {
    const fetchDesign = async () => {
      try {
        setLoading(true);
        const [designRes, categoriesRes, tagsRes, familiesRes] = await Promise.all([
          axios.get(`/api/designs/designs/${id}/`),
          axios.get('/api/designs/categories/'),
          axios.get('/api/designs/tags/'),
          axios.get('/api/designs/families/')
        ]);

        const design = designRes.data;
        
        setFormData({
          title: design.title,
          description: design.description || '',
          size: design.size || '',
          type: design.type || '',
          status: design.status,
          is_public: design.is_public,
          category_ids: design.categories ? design.categories.map(cat => cat.id) : [],
          tag_ids: design.tags ? design.tags.map(tag => tag.id) : [],
          family_ids: design.families ? design.families.map(fam => fam.id) : [],
          product_image: null,
          svg_file: null
        });
        
        // تنظیم آپشن‌ها و پیش‌نمایش‌ها
        setCategories(formatOptions(categoriesRes.data));
        setTags(formatOptions(tagsRes.data));
        setFamilies(formatOptions(familiesRes.data));
        
        // تنظیم پیش‌نمایش‌ها اگر وجود داشته باشند
        if (design.product_image) {
          setImagePreview(design.product_image);
        }
        if (design.svg_file) {
          setSvgPreview(design.svg_file);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching design:', error);
        toast.error('خطا در بارگیری اطلاعات طرح');
        navigate('/designs');
      }
    };

    fetchDesign();
  }, [id, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'file') {
      if (files && files[0]) {
        setFormData(prev => ({
          ...prev,
          [name]: files[0]
        }));
        
        // نمایش پیش‌نمایش فایل
        const reader = new FileReader();
        reader.onload = (e) => {
          if (name === 'product_image') {
            setImagePreview(e.target.result);
          } else if (name === 'svg_file') {
            setSvgPreview(e.target.result);
          }
        };
        reader.readAsDataURL(files[0]);
      }
    } else if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // مدیریت تغییرات در سلکت‌ها
  const handleSelectChange = (selectedOptions, { name }) => {
    if (name === 'family_ids') {
      setFormData(prev => ({
        ...prev,
        [name]: selectedOptions ? selectedOptions.map(option => option.value) : []
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: selectedOptions ? selectedOptions.map(option => option.value) : []
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title) {
      toast.error('عنوان طرح را وارد کنید');
      return;
    }
    
    try {
      setSubmitting(true);
      
      // FormData را می‌سازیم
      const form = new FormData();
      form.append('title', formData.title);
      form.append('description', formData.description);
      form.append('size', formData.size);
      form.append('type', formData.type);
      form.append('status', formData.status);
      form.append('is_public', formData.is_public);
      
      // اضافه کردن دسته‌بندی‌ها و تگ‌ها و خانواده‌ها با نام‌های درست
      formData.category_ids.forEach(id => {
        form.append('category_ids', id);
      });
      
      formData.tag_ids.forEach(id => {
        form.append('tag_ids', id);
      });
      
      formData.family_ids.forEach(id => {
        form.append('family_ids', id);
      });
      
      // اضافه کردن فایل‌ها در صورت تغییر
      if (formData.product_image) {
        form.append('product_image', formData.product_image);
      }
      
      if (formData.svg_file) {
        form.append('svg_file', formData.svg_file);
      }
      
      // ارسال به سرور
      const response = await axios.patch(`/api/designs/designs/${id}/`, form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast.success('طرح با موفقیت به‌روزرسانی شد');
      navigate(`/designs/${response.data.id}`);
    } catch (error) {
      console.error('Error updating design:', error);
      toast.error(error.response?.data?.detail || 'خطا در به‌روزرسانی طرح');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="sr-only">در حال بارگذاری...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-2xl font-bold mb-6">ویرایش طرح</h1>
        
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="title">
                  عنوان <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="description">
                  توضیحات
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="size">
                  اندازه
                </label>
                <input
                  type="text"
                  id="size"
                  name="size"
                  value={formData.size}
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="type">
                  نوع
                </label>
                <input
                  type="text"
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="status">
                  وضعیت
                </label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="draft">پیش‌نویس</option>
                  <option value="published">منتشر شده</option>
                  <option value="archived">بایگانی شده</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">
                  <input
                    type="checkbox"
                    name="is_public"
                    checked={formData.is_public}
                    onChange={handleChange}
                    className="mr-2 leading-tight"
                  />
                  <span className="text-sm">
                    نمایش عمومی
                  </span>
                </label>
              </div>
            </div>
            
            <div>
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="categories">
                  دسته‌بندی‌ها
                </label>
                <Select
                  isMulti
                  name="category_ids"
                  options={categories}
                  className="basic-multi-select"
                  classNamePrefix="select"
                  placeholder="دسته‌بندی‌ها را انتخاب کنید"
                  value={formatCurrentOptions(formData.category_ids, categories)}
                  onChange={(selectedOptions) => handleSelectChange(selectedOptions, { name: 'category_ids' })}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="tags">
                  برچسب‌ها
                </label>
                <Select
                  isMulti
                  name="tag_ids"
                  options={tags}
                  className="basic-multi-select"
                  classNamePrefix="select"
                  placeholder="برچسب‌ها را انتخاب کنید"
                  value={formatCurrentOptions(formData.tag_ids, tags)}
                  onChange={(selectedOptions) => handleSelectChange(selectedOptions, { name: 'tag_ids' })}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="family">
                  خانواده
                </label>
                <Select
                  isMulti
                  name="family_ids"
                  options={families}
                  className="basic-multi-select"
                  classNamePrefix="select"
                  placeholder="خانواده‌ها را انتخاب کنید"
                  value={formatCurrentOptions(formData.family_ids, families)}
                  onChange={(selectedOptions) => handleSelectChange(selectedOptions, { name: 'family_ids' })}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="product_image">
                  تصویر محصول
                </label>
                <input
                  type="file"
                  id="product_image"
                  name="product_image"
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  accept="image/*"
                />
                {imagePreview && (
                  <div className="mt-2">
                    <img src={imagePreview} alt="پیش‌نمایش تصویر" className="max-w-full h-48 object-contain" />
                  </div>
                )}
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2" htmlFor="svg_file">
                  فایل SVG
                </label>
                <input
                  type="file"
                  id="svg_file"
                  name="svg_file"
                  onChange={handleChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  accept=".svg"
                />
                {svgPreview && (
                  <div className="mt-2">
                    <img src={svgPreview} alt="پیش‌نمایش SVG" className="max-w-full h-48 object-contain" />
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-6">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={submitting}
            >
              {submitting ? 'در حال ذخیره...' : 'به‌روزرسانی طرح'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/designs/${id}`)}
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              انصراف
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default EditDesign; 