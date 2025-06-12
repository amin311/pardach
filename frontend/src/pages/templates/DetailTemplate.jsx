import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaEdit, FaPlus } from 'react-icons/fa';

// کامپوننت نمایش بخش‌های قالب
const SectionItem = ({ section }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800">{section.title}</h3>
      <p className="text-gray-600 mt-2">{section.description}</p>
      
      {section.design_inputs && section.design_inputs.length > 0 && (
        <div className="mt-4">
          <h4 className="text-md font-medium text-gray-700 mb-2">ورودی‌های طراحی:</h4>
          <ul className="space-y-2">
            {section.design_inputs.map((input) => (
              <li key={input.id} className="flex items-start">
                <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mt-2 ml-2"></span>
                <div>
                  <span className="font-medium">{input.title}</span>
                  {input.required && <span className="text-red-500 mr-1">*</span>}
                  <p className="text-gray-500 text-sm">{input.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {section.conditions && section.conditions.length > 0 && (
        <div className="mt-4">
          <h4 className="text-md font-medium text-gray-700 mb-2">شرایط انتخابی:</h4>
          <ul className="space-y-2">
            {section.conditions.map((condition) => (
              <li key={condition.id} className="flex items-start">
                <span className="inline-block w-2 h-2 rounded-full bg-green-500 mt-2 ml-2"></span>
                <div>
                  <span className="font-medium">{condition.title}</span>
                  <p className="text-gray-500 text-sm">{condition.description}</p>
                  {condition.price_modifier > 0 && (
                    <p className="text-green-600 text-sm">
                      + {condition.price_modifier.toLocaleString()} تومان
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const DetailTemplate = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplate();
  }, [id]);

  const fetchTemplate = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(`/api/templates/templates/${id}/`);
      setTemplate(response.data);
      setLoading(false);
    } catch (error) {
      toast.error('خطا در دریافت اطلاعات قالب');
      setLoading(false);
      console.error('Error fetching template:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!template) {
    return (
      <div className="text-center py-10">
        <h2 className="text-xl text-gray-700">قالب مورد نظر یافت نشد!</h2>
        <button
          onClick={() => navigate('/templates')}
          className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <FaArrowLeft className="ml-2" /> بازگشت به لیست قالب‌ها
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <button
          onClick={() => navigate('/templates')}
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <FaArrowLeft className="ml-1" /> بازگشت به لیست قالب‌ها
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
        <div className="p-6">
          <div className="flex justify-between items-start">
            <h1 className="text-2xl font-bold text-gray-800">{template.title}</h1>
            <span className="px-4 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
              قیمت پایه: {template.base_price.toLocaleString()} تومان
            </span>
          </div>
          <p className="text-gray-600 mt-4">{template.description}</p>

          <div className="mt-8">
            <Link
              to={`/templates/use/${template.id}`}
              className="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <FaPlus className="ml-2" /> استفاده از این قالب
            </Link>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">بخش‌های قالب</h2>
        {template.sections && template.sections.length > 0 ? (
          <div className="space-y-4">
            {template.sections.map((section) => (
              <SectionItem key={section.id} section={section} />
            ))}
          </div>
        ) : (
          <p className="text-gray-500">هیچ بخشی برای این قالب تعریف نشده است.</p>
        )}
      </div>

      {template.set_dimensions && template.set_dimensions.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">ابعاد قابل انتخاب</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {template.set_dimensions.map((dimension) => (
              <div key={dimension.id} className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
                <h3 className="text-md font-semibold text-gray-800">{dimension.title}</h3>
                <div className="mt-2 flex items-center text-gray-600">
                  <span>ابعاد: {dimension.width} × {dimension.height}</span>
                </div>
                {dimension.price_modifier > 0 && (
                  <p className="text-green-600 text-sm mt-2">
                    + {dimension.price_modifier.toLocaleString()} تومان
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DetailTemplate; 