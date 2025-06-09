import React, { useState, useEffect } from 'react';
import axiosInstance from './lib/axios';
import { toast } from 'react-toastify';

const SystemSettings = ({ isAdmin }) => {
  const [settings, setSettings] = useState([]);
  const [newSetting, setNewSetting] = useState({ key: '', value: '', description: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // بارگذاری تنظیمات در لود اولیه صفحه
  useEffect(() => {
    if (isAdmin) {
      fetchSettings();
    }
  }, [isAdmin]);

  // دریافت تنظیمات از سرور
  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/core/settings/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setSettings(response.data);
      setError(null);
    } catch (err) {
      setError('خطا در بارگذاری تنظیمات');
      toast.error('خطا در بارگذاری تنظیمات سیستم');
    } finally {
      setLoading(false);
    }
  };

  // افزودن تنظیم جدید
  const handleAddSetting = async (e) => {
    e.preventDefault();
    if (!newSetting.key || !newSetting.value) {
      toast.warning('کلید و مقدار الزامی است');
      return;
    }

    try {
      // تبدیل مقدار به JSON در صورت نیاز
      let parsedValue = newSetting.value;
      try {
        parsedValue = JSON.parse(newSetting.value);
      } catch {
        // اگر JSON نبود، همان مقدار رشته‌ای استفاده می‌شود
      }

      const response = await axiosInstance.post('/api/core/settings/', 
        { ...newSetting, value: parsedValue },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      toast.success('تنظیم با موفقیت اضافه شد');
      setNewSetting({ key: '', value: '', description: '' });
      fetchSettings();
    } catch (err) {
      toast.error('خطا در ذخیره تنظیم جدید');
    }
  };

  // ویرایش تنظیم موجود
  const handleUpdateSetting = async (key, value) => {
    try {
      let parsedValue = value;
      // اگر مقدار به صورت رشته است، تلاش برای تبدیل به JSON
      if (typeof value === 'string') {
        try {
          parsedValue = JSON.parse(value);
        } catch {
          // اگر JSON نبود، همان مقدار رشته‌ای استفاده می‌شود
        }
      }

      await axiosInstance.put(`/api/core/settings/${key}/`, 
        { value: parsedValue },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      toast.success('تنظیم با موفقیت بروزرسانی شد');
      fetchSettings();
    } catch (err) {
      toast.error('خطا در بروزرسانی تنظیم');
    }
  };

  // رندر صفحه عدم دسترسی برای غیر ادمین
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="text-center p-6 bg-gray-100 rounded-lg shadow">
          <div className="text-5xl text-red-500 mb-4">🔒</div>
          <h2 className="text-xl font-bold mb-2">دسترسی محدود</h2>
          <p className="text-gray-600">شما به این بخش دسترسی ندارید.</p>
        </div>
      </div>
    );
  }

  // نمایش لودینگ
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6 text-center">مدیریت تنظیمات سیستم</h1>
      
      {/* فرم افزودن تنظیم جدید */}
      <div className="bg-white p-5 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <span className="ml-2">➕</span>
          افزودن تنظیم جدید
        </h2>
        <form onSubmit={handleAddSetting}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">کلید</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 rounded-md" 
                value={newSetting.key}
                onChange={(e) => setNewSetting({...newSetting, key: e.target.value})}
                placeholder="مثال: max_file_size_mb"
              />
              <p className="text-xs text-gray-500 mt-1">نام منحصر به فرد برای شناسایی تنظیم</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">مقدار</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 rounded-md" 
                value={newSetting.value}
                onChange={(e) => setNewSetting({...newSetting, value: e.target.value})}
                placeholder="مثال: 5 یا [\"jpg\",\"png\"]"
              />
              <p className="text-xs text-gray-500 mt-1">یک عدد، رشته یا آرایه به فرمت JSON</p>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">توضیحات</label>
            <textarea 
              className="w-full p-2 border border-gray-300 rounded-md" 
              value={newSetting.description}
              onChange={(e) => setNewSetting({...newSetting, description: e.target.value})}
              placeholder="توضیحات مربوط به این تنظیم"
              rows="2"
            ></textarea>
          </div>
          <button 
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition"
          >
            ذخیره تنظیم
          </button>
        </form>
      </div>
      
      {/* لیست تنظیمات موجود */}
      <div className="bg-white p-5 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <span className="ml-2">⚙️</span>
          تنظیمات موجود
        </h2>
        
        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-md mb-4">
            {error}
          </div>
        )}
        
        {settings.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            هیچ تنظیمی یافت نشد
          </div>
        ) : (
          <div className="space-y-4">
            {settings.map((setting) => (
              <div key={setting.key} className="border p-4 rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">{setting.key}</span>
                </div>
                <div className="mb-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">مقدار فعلی</label>
                  <input 
                    type="text" 
                    className="w-full p-2 border border-gray-300 rounded-md"
                    defaultValue={JSON.stringify(setting.value)}
                    onBlur={(e) => handleUpdateSetting(setting.key, e.target.value)}
                  />
                </div>
                <p className="text-sm text-gray-600">{setting.description || 'بدون توضیحات'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemSettings; 