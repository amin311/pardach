import React, { useState, useEffect } from 'react';
import axiosInstance from '../../lib/axios';
import { toast } from 'react-toastify';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Select from 'react-select';

const CreateOrder = ({ userId, isAdmin }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    status: 'pending',
    notes: '',
    items: [{ design_id: '', user_template_id: '', quantity: 1 }]
  });
  
  const [designs, setDesigns] = useState([]);
  const [userTemplates, setUserTemplates] = useState([]);
  const [loadingDesigns, setLoadingDesigns] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        setLoadingDesigns(true);
        setLoadingTemplates(true);
        
        // طرح‌ها را دریافت می‌کنیم
        const designsResponse = await axiosInstance.get('/api/designs/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setDesigns(designsResponse.data.map(design => ({
          value: design.id,
          label: design.title,
          price: design.price
        })));
        
        setLoadingDesigns(false);
        
        // قالب‌های کاربر را دریافت می‌کنیم
        const templatesResponse = await axiosInstance.get('/api/templates/user-templates/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        setUserTemplates(templatesResponse.data.map(template => ({
          value: template.id,
          label: template.name || `قالب #${template.id.substring(0, 6)}`,
          price: template.final_price
        })));
        
        setLoadingTemplates(false);
      } catch (error) {
        toast.error('خطا در دریافت اطلاعات');
        setLoadingDesigns(false);
        setLoadingTemplates(false);
      }
    };
    
    fetchOptions();
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { design_id: '', user_template_id: '', quantity: 1 }]
    });
  };

  const handleRemoveItem = (index) => {
    if (formData.items.length > 1) {
      const updatedItems = [...formData.items];
      updatedItems.splice(index, 1);
      setFormData({ ...formData, items: updatedItems });
    } else {
      toast.warning('حداقل یک آیتم باید وجود داشته باشد');
    }
  };

  const handleItemChange = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    
    // اگر design انتخاب شد، مقدار user_template را خالی می‌کنیم و برعکس
    if (field === 'design_id' && value) {
      updatedItems[index].user_template_id = '';
    } else if (field === 'user_template_id' && value) {
      updatedItems[index].design_id = '';
    }
    
    setFormData({ ...formData, items: updatedItems });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // حداقل یکی از آیتم‌ها باید مقدار داشته باشد
    const hasValidItems = formData.items.some(item => 
      (item.design_id || item.user_template_id) && item.quantity > 0
    );
    
    if (!hasValidItems) {
      toast.error('حداقل یک طرح یا قالب باید انتخاب شود');
      return;
    }
    
    try {
      setLoading(true);
      
      // ایجاد سفارش
      const orderResponse = await axiosInstance.post('/api/orders/', {
        status: formData.status,
        notes: formData.notes
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      const orderId = orderResponse.data.id;
      
      // افزودن آیتم‌ها به سفارش
      for (const item of formData.items) {
        if ((item.design_id || item.user_template_id) && item.quantity > 0) {
          await axiosInstance.post(`/api/orders/${orderId}/items/`, {
            design_id: item.design_id || null,
            user_template_id: item.user_template_id || null,
            quantity: item.quantity
          }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          });
        }
      }
      
      setLoading(false);
      toast.success('سفارش با موفقیت ثبت شد');
      navigate(`/orders/${orderId}`);
    } catch (error) {
      setLoading(false);
      toast.error('خطا در ثبت سفارش');
      console.error(error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-plus-circle"></i> ایجاد سفارش جدید
        </h2>
        
        <Link
          to="/orders"
          className="bg-gray-500 text-white px-3 py-1 rounded-md flex items-center gap-1 hover:bg-gray-600 transition-all"
        >
          <i className="fas fa-arrow-right"></i> بازگشت
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block font-medium mb-2">وضعیت سفارش</label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pending">در انتظار</option>
                <option value="processing">در حال انجام</option>
                <option value="completed">تکمیل‌شده</option>
                <option value="cancelled">لغو شده</option>
              </select>
            </div>
            
            <div>
              <label className="block font-medium mb-2">یادداشت‌ها</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="4"
                placeholder="یادداشت‌های سفارش را وارد کنید..."
              ></textarea>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <i className="fas fa-box"></i> آیتم‌های سفارش
              </h3>
              
              <button
                type="button"
                onClick={handleAddItem}
                className="bg-blue-500 text-white px-3 py-1 rounded-md flex items-center gap-1 hover:bg-blue-600 transition-all"
              >
                <i className="fas fa-plus"></i> افزودن آیتم
              </button>
            </div>
            
            {formData.items.map((item, index) => (
              <motion.div
                key={index}
                className="mb-4 p-4 bg-gray-50 rounded-md border border-gray-200"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-medium">آیتم {index + 1}</h4>
                  
                  <button
                    type="button"
                    onClick={() => handleRemoveItem(index)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">انتخاب طرح</label>
                    <Select
                      value={item.design_id ? designs.find(d => d.value === item.design_id) : null}
                      onChange={(option) => handleItemChange(index, 'design_id', option ? option.value : '')}
                      options={designs}
                      placeholder="انتخاب طرح..."
                      isLoading={loadingDesigns}
                      isClearable
                      isDisabled={!!item.user_template_id}
                      className="text-sm"
                      isRtl={true}
                      noOptionsMessage={() => "طرحی یافت نشد"}
                      formatOptionLabel={option => (
                        <div className="flex justify-between items-center">
                          <span>{option.label}</span>
                          {option.price && <span className="text-gray-500">{Number(option.price).toLocaleString()} تومان</span>}
                        </div>
                      )}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">انتخاب قالب</label>
                    <Select
                      value={item.user_template_id ? userTemplates.find(t => t.value === item.user_template_id) : null}
                      onChange={(option) => handleItemChange(index, 'user_template_id', option ? option.value : '')}
                      options={userTemplates}
                      placeholder="انتخاب قالب..."
                      isLoading={loadingTemplates}
                      isClearable
                      isDisabled={!!item.design_id}
                      className="text-sm"
                      isRtl={true}
                      noOptionsMessage={() => "قالبی یافت نشد"}
                      formatOptionLabel={option => (
                        <div className="flex justify-between items-center">
                          <span>{option.label}</span>
                          {option.price && <span className="text-gray-500">{Number(option.price).toLocaleString()} تومان</span>}
                        </div>
                      )}
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">تعداد</label>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 1)}
                    className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`px-6 py-3 rounded-md flex items-center gap-2 ${
                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'
              } text-white transition-all`}
            >
              {loading ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white rounded-full border-t-transparent"></div>
                  در حال ثبت...
                </>
              ) : (
                <>
                  <i className="fas fa-check"></i>
                  ثبت سفارش
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </motion.div>
  );
};

export default CreateOrder; 