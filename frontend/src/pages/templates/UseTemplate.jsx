import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaSave, FaTimesCircle, FaCheckCircle } from 'react-icons/fa';

// کامپوننت مرحله به مرحله (Stepper)
const Stepper = ({ steps, currentStep }) => {
  return (
    <div className="flex items-center justify-between mb-8">
      {steps.map((step, index) => (
        <div key={index} className="flex flex-col items-center relative">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center ${
              index < currentStep
                ? 'bg-green-500 text-white'
                : index === currentStep
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {index < currentStep ? (
              <FaCheckCircle />
            ) : (
              <span>{index + 1}</span>
            )}
          </div>
          <span
            className={`mt-2 text-sm ${
              index <= currentStep ? 'text-gray-700 font-medium' : 'text-gray-400'
            }`}
          >
            {step}
          </span>
          {index < steps.length - 1 && (
            <div
              className={`absolute top-4 w-full h-0.5 right-1/2 ${
                index < currentStep ? 'bg-green-500' : 'bg-gray-200'
              }`}
              style={{ width: '100%', transform: 'translateX(50%)' }}
            ></div>
          )}
        </div>
      ))}
    </div>
  );
};

// کامپوننت ورودی براساس نوع ورودی
const InputField = ({ input, value, onChange }) => {
  switch (input.input_type) {
    case 'TEXT':
      return (
        <input
          type="text"
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          required={input.required}
        />
      );
    case 'TEXTAREA':
      return (
        <textarea
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[100px]"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          required={input.required}
        />
      );
    case 'NUMBER':
      return (
        <input
          type="number"
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          required={input.required}
        />
      );
    case 'COLOR':
      return (
        <div className="flex items-center">
          <input
            type="color"
            className="w-12 h-10 border border-gray-300 rounded-md"
            value={value || '#000000'}
            onChange={(e) => onChange(e.target.value)}
            required={input.required}
          />
          <input
            type="text"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mr-2"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder="#000000"
            required={input.required}
          />
        </div>
      );
    default:
      return (
        <input
          type="text"
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          required={input.required}
        />
      );
  }
};

// کامپوننت بخش قالب
const TemplateSection = ({ section, userSection, onInputChange, onConditionChange }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{section.title}</h3>
      <p className="text-gray-600 mb-6">{section.description}</p>

      {section.design_inputs && section.design_inputs.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-700 mb-4">ورودی‌های طراحی</h4>
          <div className="space-y-4">
            {section.design_inputs.map((input) => {
              const userInput = userSection?.user_design_inputs?.find(
                (i) => i.design_input === input.id
              );
              return (
                <div key={input.id} className="mb-4">
                  <label className="block text-gray-700 mb-2">
                    {input.title}
                    {input.required && <span className="text-red-500 mr-1">*</span>}
                  </label>
                  {input.description && (
                    <p className="text-gray-500 text-sm mb-2">{input.description}</p>
                  )}
                  <InputField
                    input={input}
                    value={userInput?.value || ''}
                    onChange={(value) => onInputChange(section.id, input.id, value)}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {section.conditions && section.conditions.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-4">شرایط انتخابی</h4>
          <div className="space-y-3">
            {section.conditions.map((condition) => {
              const userCondition = userSection?.user_conditions?.find(
                (c) => c.condition === condition.id
              );
              return (
                <div key={condition.id} className="flex items-start">
                  <input
                    type="checkbox"
                    id={`condition-${condition.id}`}
                    className="mt-1 ml-3"
                    checked={userCondition?.is_selected || false}
                    onChange={(e) =>
                      onConditionChange(section.id, condition.id, e.target.checked)
                    }
                  />
                  <div>
                    <label
                      htmlFor={`condition-${condition.id}`}
                      className="text-gray-700 font-medium cursor-pointer"
                    >
                      {condition.title}
                    </label>
                    {condition.description && (
                      <p className="text-gray-500 text-sm">{condition.description}</p>
                    )}
                    {condition.price_modifier > 0 && (
                      <p className="text-green-600 text-sm">
                        + {condition.price_modifier.toLocaleString()} تومان
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// کامپوننت انتخاب ابعاد
const DimensionsSelector = ({ dimensions, selectedDimension, onChange }) => {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">انتخاب ابعاد</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dimensions.map((dimension) => (
          <div
            key={dimension.id}
            className={`bg-white rounded-lg p-4 border cursor-pointer transition-all ${
              selectedDimension === dimension.id
                ? 'border-blue-500 shadow-md'
                : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => onChange(dimension.id)}
          >
            <div className="flex items-center">
              <input
                type="radio"
                id={`dim-${dimension.id}`}
                name="dimension"
                checked={selectedDimension === dimension.id}
                onChange={() => onChange(dimension.id)}
                className="ml-2"
              />
              <label htmlFor={`dim-${dimension.id}`} className="cursor-pointer w-full">
                <h4 className="font-medium text-gray-800">{dimension.title}</h4>
                <div className="mt-1 text-gray-600 text-sm">
                  ابعاد: {dimension.width} × {dimension.height}
                </div>
                {dimension.price_modifier > 0 && (
                  <p className="text-green-600 text-sm mt-1">
                    + {dimension.price_modifier.toLocaleString()} تومان
                  </p>
                )}
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// کامپوننت مرحله نهایی
const FinalStep = ({ template, userTemplate, finalPrice }) => {
  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">خلاصه سفارش</h3>
        <div className="mb-4">
          <h4 className="font-medium text-gray-700">عنوان قالب:</h4>
          <p className="text-gray-800">{template.title}</p>
        </div>
        <div className="mb-4">
          <h4 className="font-medium text-gray-700">قیمت پایه:</h4>
          <p className="text-gray-800">{template.base_price.toLocaleString()} تومان</p>
        </div>
        {userTemplate.set_dimensions && (
          <div className="mb-4">
            <h4 className="font-medium text-gray-700">ابعاد انتخاب شده:</h4>
            <p className="text-gray-800">
              {
                template.set_dimensions.find((d) => d.id === userTemplate.set_dimensions)
                  ?.title
              }
            </p>
          </div>
        )}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <h4 className="text-xl font-bold text-gray-800">قیمت نهایی:</h4>
            <p className="text-2xl font-bold text-blue-600">
              {finalPrice.toLocaleString()} تومان
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">نکات مهم</h3>
        <ul className="space-y-2 text-gray-700">
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mt-2 ml-2"></span>
            <span>پس از ثبت سفارش، کارشناسان ما با شما تماس خواهند گرفت.</span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mt-2 ml-2"></span>
            <span>قیمت نهایی ممکن است با توجه به جزئیات بیشتر تغییر کند.</span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 mt-2 ml-2"></span>
            <span>
              زمان تحویل کار پس از تایید نهایی طرح و پرداخت، بین ۵ تا ۱۰ روز کاری خواهد
              بود.
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

// کامپوننت اصلی استفاده از قالب
const UseTemplate = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);
  const [userTemplate, setUserTemplate] = useState(null);
  const [finalPrice, setFinalPrice] = useState(0);
  
  // مراحل استفاده از قالب
  const steps = ['انتخاب ابعاد', 'تکمیل اطلاعات', 'بررسی نهایی'];

  useEffect(() => {
    fetchTemplate();
  }, [id]);

  const fetchTemplate = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/templates/templates/${id}/`);
      const templateData = response.data;
      setTemplate(templateData);
      
      // ایجاد ساختار اولیه قالب کاربر
      const initialUserTemplate = {
        template: templateData.id,
        title: templateData.title,
        status: 'DRAFT',
        user_sections: templateData.sections.map(section => ({
          section: section.id,
          title: section.title,
          user_design_inputs: section.design_inputs.map(input => ({
            design_input: input.id,
            value: ''
          })),
          user_conditions: section.conditions.map(condition => ({
            condition: condition.id,
            is_selected: false
          }))
        }))
      };
      
      setUserTemplate(initialUserTemplate);
      setFinalPrice(templateData.base_price);
      setLoading(false);
    } catch (error) {
      toast.error('خطا در دریافت اطلاعات قالب');
      setLoading(false);
      console.error('Error fetching template:', error);
    }
  };

  // محاسبه قیمت نهایی
  const calculateFinalPrice = (updatedUserTemplate) => {
    if (!template) return 0;
    
    let price = template.base_price;
    
    // اضافه کردن قیمت ابعاد انتخاب شده
    if (updatedUserTemplate.set_dimensions) {
      const selectedDimension = template.set_dimensions.find(
        d => d.id === updatedUserTemplate.set_dimensions
      );
      if (selectedDimension) {
        price += selectedDimension.price_modifier;
      }
    }
    
    // اضافه کردن قیمت شرایط انتخاب شده
    updatedUserTemplate.user_sections.forEach(userSection => {
      userSection.user_conditions.forEach(userCondition => {
        if (userCondition.is_selected) {
          const section = template.sections.find(s => s.id === userSection.section);
          if (section) {
            const condition = section.conditions.find(c => c.id === userCondition.condition);
            if (condition) {
              price += condition.price_modifier;
            }
          }
        }
      });
    });
    
    return price;
  };

  // تغییر ورودی‌های طراحی
  const handleInputChange = (sectionId, inputId, value) => {
    const updatedUserTemplate = { ...userTemplate };
    const sectionIndex = updatedUserTemplate.user_sections.findIndex(
      s => s.section === sectionId
    );
    
    if (sectionIndex !== -1) {
      const inputIndex = updatedUserTemplate.user_sections[sectionIndex].user_design_inputs.findIndex(
        i => i.design_input === inputId
      );
      
      if (inputIndex !== -1) {
        updatedUserTemplate.user_sections[sectionIndex].user_design_inputs[inputIndex].value = value;
        setUserTemplate(updatedUserTemplate);
      }
    }
  };

  // تغییر شرایط
  const handleConditionChange = (sectionId, conditionId, isSelected) => {
    const updatedUserTemplate = { ...userTemplate };
    const sectionIndex = updatedUserTemplate.user_sections.findIndex(
      s => s.section === sectionId
    );
    
    if (sectionIndex !== -1) {
      const conditionIndex = updatedUserTemplate.user_sections[sectionIndex].user_conditions.findIndex(
        c => c.condition === conditionId
      );
      
      if (conditionIndex !== -1) {
        updatedUserTemplate.user_sections[sectionIndex].user_conditions[conditionIndex].is_selected = isSelected;
        setUserTemplate(updatedUserTemplate);
        
        // به‌روزرسانی قیمت نهایی
        const newFinalPrice = calculateFinalPrice(updatedUserTemplate);
        setFinalPrice(newFinalPrice);
      }
    }
  };

  // تغییر ابعاد
  const handleDimensionChange = (dimensionId) => {
    const updatedUserTemplate = { ...userTemplate, set_dimensions: dimensionId };
    setUserTemplate(updatedUserTemplate);
    
    // به‌روزرسانی قیمت نهایی
    const newFinalPrice = calculateFinalPrice(updatedUserTemplate);
    setFinalPrice(newFinalPrice);
  };

  // اعتبارسنجی مرحله فعلی
  const validateCurrentStep = () => {
    if (currentStep === 0) {
      // اعتبارسنجی انتخاب ابعاد (اگر ابعاد وجود دارد، باید انتخاب شده باشد)
      if (template.set_dimensions && template.set_dimensions.length > 0 && !userTemplate.set_dimensions) {
        toast.error('لطفاً یک ابعاد را انتخاب کنید');
        return false;
      }
      return true;
    } else if (currentStep === 1) {
      // اعتبارسنجی ورودی‌های ضروری
      let isValid = true;
      let errorMessage = '';
      
      userTemplate.user_sections.forEach(userSection => {
        const section = template.sections.find(s => s.id === userSection.section);
        
        section.design_inputs.forEach(input => {
          if (input.required) {
            const userInput = userSection.user_design_inputs.find(
              i => i.design_input === input.id
            );
            
            if (!userInput || !userInput.value || userInput.value.trim() === '') {
              isValid = false;
              errorMessage = `لطفاً فیلد "${input.title}" در بخش "${section.title}" را تکمیل کنید`;
            }
          }
        });
      });
      
      if (!isValid) {
        toast.error(errorMessage);
      }
      
      return isValid;
    }
    
    return true;
  };

  // مرحله بعدی
  const nextStep = () => {
    if (validateCurrentStep()) {
      setCurrentStep(currentStep + 1);
    }
  };

  // مرحله قبلی
  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // ثبت نهایی قالب کاربر
  const submitUserTemplate = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/templates/user-templates/', {
        ...userTemplate,
        final_price: finalPrice
      });
      
      setLoading(false);
      toast.success('قالب شما با موفقیت ثبت شد');
      navigate(`/user-templates/${response.data.id}`);
    } catch (error) {
      setLoading(false);
      toast.error('خطا در ثبت قالب');
      console.error('Error submitting user template:', error);
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
          <h1 className="text-2xl font-bold text-gray-800">استفاده از قالب: {template.title}</h1>
          <p className="text-gray-600 mt-2">{template.description}</p>
        </div>
      </div>

      <Stepper steps={steps} currentStep={currentStep} />

      <div className="bg-white rounded-lg shadow-md overflow-hidden p-6 mb-6">
        {currentStep === 0 && template.set_dimensions && template.set_dimensions.length > 0 && (
          <DimensionsSelector
            dimensions={template.set_dimensions}
            selectedDimension={userTemplate.set_dimensions}
            onChange={handleDimensionChange}
          />
        )}

        {currentStep === 1 && (
          <div>
            {template.sections.map((section) => {
              const userSection = userTemplate.user_sections.find(
                (s) => s.section === section.id
              );
              return (
                <TemplateSection
                  key={section.id}
                  section={section}
                  userSection={userSection}
                  onInputChange={handleInputChange}
                  onConditionChange={handleConditionChange}
                />
              );
            })}
          </div>
        )}

        {currentStep === 2 && (
          <FinalStep
            template={template}
            userTemplate={userTemplate}
            finalPrice={finalPrice}
          />
        )}
      </div>

      <div className="flex justify-between">
        {currentStep > 0 ? (
          <button
            onClick={prevStep}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            مرحله قبل
          </button>
        ) : (
          <div></div>
        )}

        {currentStep < steps.length - 1 ? (
          <button
            onClick={nextStep}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            مرحله بعد
          </button>
        ) : (
          <button
            onClick={submitUserTemplate}
            disabled={loading}
            className="inline-flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            {loading ? (
              <span className="ml-2 animate-spin">&#9696;</span>
            ) : (
              <FaSave className="ml-2" />
            )}
            ثبت نهایی
          </button>
        )}
      </div>
    </div>
  );
};

export default UseTemplate; 