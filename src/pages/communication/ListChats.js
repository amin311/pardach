import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ListChats = ({ userId, isAdmin }) => {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // دریافت لیست چت‌ها
    axios.get('/api/communication/chats/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
      .then(res => {
        setChats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching chats:', err);
        toast.error('خطا در بارگذاری چت‌ها');
        setLoading(false);
      });
  }, []);

  // حذف چت
  const handleDeleteChat = (chatId) => {
    if (window.confirm('آیا از حذف این چت اطمینان دارید؟')) {
      axios.delete(`/api/communication/chats/${chatId}/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
        .then(() => {
          setChats(chats.filter(chat => chat.id !== chatId));
          toast.success('چت با موفقیت حذف شد');
        })
        .catch(err => {
          console.error('Error deleting chat:', err);
          toast.error('خطا در حذف چت');
        });
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <i className="fas fa-comments"></i> لیست چت‌ها
        </h2>
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
        <i className="fas fa-comments"></i> لیست چت‌ها
      </h2>

      <div className="mb-6 flex justify-end">
        <Link
          to="/chats/create"
          className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md flex items-center gap-2 transition-colors"
        >
          <i className="fas fa-plus"></i>
          ایجاد چت جدید
        </Link>
      </div>

      {chats.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-500">هیچ چتی یافت نشد</p>
          <Link
            to="/chats/create"
            className="text-blue-500 mt-4 inline-block hover:underline"
          >
            ایجاد چت جدید
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {chats.map((chat) => (
            <motion.div
              key={chat.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white p-4 rounded-lg shadow"
            >
              <div className="mb-4">
                <h3 className="font-bold text-lg flex items-center justify-between">
                  <span>{chat.title || 'چت بدون عنوان'}</span>
                  {chat.unread_messages_count > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                      {chat.unread_messages_count}
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-500">
                  شرکت‌کنندگان: {chat.participants.map(p => p.username).join(', ')}
                </p>
                {chat.business && (
                  <p className="text-sm text-gray-500">
                    کسب‌وکار: {chat.business.name}
                  </p>
                )}
                <p className="text-sm text-gray-500">
                  تاریخ ایجاد: {chat.created_at_jalali}
                </p>
              </div>

              <div className="flex justify-between">
                <Link
                  to={`/chats/${chat.id}`}
                  className="bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded-md flex items-center gap-1 text-sm transition-colors"
                >
                  <i className="fas fa-eye"></i>
                  مشاهده چت
                </Link>
                <button
                  onClick={() => handleDeleteChat(chat.id)}
                  className="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded-md flex items-center gap-1 text-sm transition-colors"
                >
                  <i className="fas fa-trash"></i>
                  حذف
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ListChats; 