import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const DetailBusiness = ({ userId, isAdmin }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [users, setUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    const fetchBusinessData = async () => {
      try {
        // دریافت اطلاعات کسب‌وکار
        const businessResponse = await axios.get(`/api/business/businesses/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setBusiness(businessResponse.data);

        // دریافت کاربران کسب‌وکار
        const usersResponse = await axios.get(`/api/business/businesses/${id}/users/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setUsers(usersResponse.data);

        // دریافت فعالیت‌های کسب‌وکار
        const activitiesResponse = await axios.get(`/api/business/businesses/${id}/activities/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setActivities(activitiesResponse.data);

        setLoading(false);
      } catch (error) {
        toast.error('خطا در بارگذاری اطلاعات کسب‌وکار');
        setLoading(false);
        // در صورت خطا 404 کاربر به صفحه لیست برگردانده شود
        if (error.response && error.response.status === 404) {
          navigate('/businesses');
        }
      }
    };

    fetchBusinessData();
  }, [id, navigate]);

  const handleDelete = async () => {
    if (window.confirm('آیا از حذف این کسب‌وکار مطمئن هستید؟')) {
      try {
        await axios.delete(`/api/business/businesses/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        toast.success('کسب‌وکار با موفقیت حذف شد');
        navigate('/businesses');
      } catch (error) {
        toast.error('خطا در حذف کسب‌وکار');
      }
    }
  };

  const activityTypeMap = {
    'design_sale': 'فروش طرح',
    'template_sale': 'فروش قالب',
    'order_processed': 'پردازش سفارش'
  };

  const roleMap = {
    'manager': 'مدیر',
    'employee': 'کارمند'
  };

  if (loading) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!business) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-500">کسب‌وکار مورد نظر یافت نشد</p>
          <Link to="/businesses" className="text-blue-500 mt-4 inline-block">
            بازگشت به لیست کسب‌وکارها
          </Link>
        </div>
      </div>
    );
  }

  const canEdit = business.owner?.id === userId || isAdmin;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-3xl mx-auto"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-briefcase"></i> {business.name}
        </h2>
        <div className="flex items-center gap-3">
          <Link
            to="/businesses"
            className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <i className="fas fa-arrow-right"></i> بازگشت
          </Link>
          {canEdit && (
            <>
              <Link
                to={`/businesses/edit/${business.id}`}
                className="bg-yellow-500 hover:bg-yellow-600 text-white py-1 px-3 rounded-md flex items-center gap-1 transition-colors"
              >
                <i className="fas fa-edit"></i> ویرایش
              </Link>
              <button
                onClick={handleDelete}
                className="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded-md flex items-center gap-1 transition-colors"
              >
                <i className="fas fa-trash"></i> حذف
              </button>
            </>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="border-b">
          <div className="flex">
            <button
              className={`py-3 px-6 text-sm font-medium transition-colors ${
                activeTab === 'general' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('general')}
            >
              <i className="fas fa-info-circle mr-1"></i> اطلاعات کلی
            </button>
            <button
              className={`py-3 px-6 text-sm font-medium transition-colors ${
                activeTab === 'users' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('users')}
            >
              <i className="fas fa-users mr-1"></i> کاربران ({users.length})
            </button>
            <button
              className={`py-3 px-6 text-sm font-medium transition-colors ${
                activeTab === 'activities' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('activities')}
            >
              <i className="fas fa-chart-line mr-1"></i> فعالیت‌ها ({activities.length})
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* اطلاعات کلی */}
          {activeTab === 'general' && (
            <div>
              <div className="flex flex-col md:flex-row gap-6">
                <div className="md:w-1/3">
                  {business.logo ? (
                    <img
                      src={business.logo}
                      alt={business.name}
                      className="w-full h-48 object-cover rounded-md"
                    />
                  ) : (
                    <div className="w-full h-48 bg-blue-100 rounded-md flex items-center justify-center">
                      <i className="fas fa-briefcase text-blue-500 text-5xl"></i>
                    </div>
                  )}
                </div>
                <div className="md:w-2/3">
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">نام کسب‌وکار:</p>
                      <p className="font-medium">{business.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">اسلاگ:</p>
                      <p className="font-medium">{business.slug}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">وضعیت:</p>
                      <p className="font-medium">
                        {business.status === 'active' ? 'فعال' : 
                         business.status === 'pending' ? 'در انتظار تأیید' : 'غیرفعال'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">مالک:</p>
                      <p className="font-medium">
                        {business.owner?.username || 'نامشخص'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">تاریخ ایجاد:</p>
                      <p className="font-medium">{business.created_at_jalali}</p>
                    </div>
                  </div>
                </div>
              </div>

              {business.description && (
                <div className="mt-6">
                  <p className="text-sm text-gray-500 mb-2">توضیحات:</p>
                  <p className="bg-gray-50 p-4 rounded-md whitespace-pre-wrap">
                    {business.description}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* کاربران */}
          {activeTab === 'users' && (
            <div>
              {users.length === 0 ? (
                <p className="text-center text-gray-500 py-4">هیچ کاربری برای این کسب‌وکار تعریف نشده است</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          نام کاربری
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          نقش
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          تاریخ عضویت
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="text-sm font-medium text-gray-900">
                                {user.user?.username || 'نامشخص'}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              user.role === 'manager' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {roleMap[user.role] || user.role}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.created_at_jalali}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* فعالیت‌ها */}
          {activeTab === 'activities' && (
            <div>
              {activities.length === 0 ? (
                <p className="text-center text-gray-500 py-4">هیچ فعالیتی برای این کسب‌وکار ثبت نشده است</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          نوع فعالیت
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          مرتبط با
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          تاریخ
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {activities.map((activity) => (
                        <tr key={activity.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              activity.activity_type === 'design_sale' ? 'bg-purple-100 text-purple-800' : 
                              activity.activity_type === 'template_sale' ? 'bg-indigo-100 text-indigo-800' : 
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {activityTypeMap[activity.activity_type] || activity.activity_type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {activity.design ? `طرح: ${activity.design.title || activity.design.id}` : 
                             activity.template ? `قالب: ${activity.template.title || activity.template.id}` : 
                             activity.order ? `سفارش: ${activity.order.id}` : 'نامشخص'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {activity.created_at_jalali}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default DetailBusiness; 