import React, { useState, useEffect, useRef } from 'react';
import axiosInstance from '../../api/axiosInstance';
import { toast } from 'react-toastify';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const ChatPage = ({ userId }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(true);
  const [sending, setSending] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    // دریافت اطلاعات چت
    axiosInstance.get(`/api/communication/chats/${id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        setChat(res.data);
      })
      .catch(err => {
        console.error('Error fetching chat:', err);
        toast.error('خطا در بارگذاری اطلاعات چت');
        navigate('/chats');
      });

    // دریافت پیام‌های چت
    axiosInstance.get(`/api/communication/chats/${id}/messages/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        setMessages(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching messages:', err);
        toast.error('خطا در بارگذاری پیام‌ها');
        setLoading(false);
      });

    // اتصال به WebSocket
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    wsRef.current = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${id}/`);

    wsRef.current.onopen = () => {
      console.log('WebSocket connection established');
      setConnecting(false);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        toast.error(data.error);
        return;
      }

      if (data.type === 'chat' && data.message) {
        setMessages(prevMessages => [...prevMessages, {
          id: data.message.id,
          content: data.message.content,
          sender: { username: data.message.sender },
          created_at_jalali: data.message.created_at || data.message.timestamp
        }]);
      } else if (data.type === 'system' && data.message) {
        toast.info(data.message.content);
      }
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket connection closed');
      setConnecting(false);
      toast.warning('اتصال قطع شد. در حال تلاش برای اتصال مجدد...');
      
      // تلاش مجدد برای اتصال پس از 5 ثانیه
      setTimeout(() => {
        if (wsRef.current.readyState === WebSocket.CLOSED) {
          window.location.reload();
        }
      }, 5000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnecting(false);
      toast.error('خطا در اتصال به سرور چت');
    };

    // بستن اتصال WebSocket در زمان خروج
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [id, navigate]);

  // اسکرول به آخرین پیام
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // علامت‌گذاری پیام‌ها به‌عنوان خوانده‌شده
  useEffect(() => {
    if (!loading && messages.length > 0) {
      messages.forEach(message => {
        if (!message.is_read && message.sender?.id !== userId) {
          axiosInstance.post(`/api/communication/messages/${message.id}/read/`, {}, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          }).catch(err => console.error('Error marking message as read:', err));
        }
      });
    }
  }, [messages, loading, userId]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    setSending(true);
    try {
      wsRef.current.send(JSON.stringify({
        content: newMessage,
        sender_id: userId
      }));
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('خطا در ارسال پیام');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center gap-2">
          <i className="fas fa-comments"></i> چت
        </h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
            <div className="h-96 bg-gray-100 rounded-lg mb-4"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 max-w-3xl mx-auto"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <i className="fas fa-comments"></i> {chat?.title || 'چت'}
        </h2>
        <Link
          to="/chats"
          className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <i className="fas fa-arrow-right"></i> بازگشت به لیست چت‌ها
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* اطلاعات شرکت‌کنندگان */}
        <div className="bg-blue-50 p-4 border-b">
          <p className="text-sm font-medium">
            شرکت‌کنندگان: {chat?.participants.map(p => p.username).join(', ')}
          </p>
          {chat?.business && (
            <p className="text-sm font-medium mt-1">
              کسب‌وکار: {chat.business.name}
            </p>
          )}
        </div>

        {/* پیام‌ها */}
        <div className="h-96 overflow-y-auto p-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <i className="fas fa-comments text-4xl mb-2 block"></i>
              <p>هنوز پیامی ارسال نشده است</p>
              <p className="text-sm mt-2">اولین پیام را ارسال کنید</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`mb-4 flex ${
                  message.sender?.id === userId ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md rounded-lg p-3 ${
                    message.sender?.id === userId 
                      ? 'bg-blue-500 text-white rounded-tr-none' 
                      : 'bg-gray-200 text-gray-800 rounded-tl-none'
                  }`}
                >
                  <div className="font-bold text-xs mb-1">
                    {message.sender?.username || 'ناشناس'}
                  </div>
                  <div className="text-sm break-words">{message.content}</div>
                  <div className="text-xs mt-1 opacity-75 text-right">
                    {message.created_at_jalali}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* فرم ارسال پیام */}
        <div className="p-4 border-t">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="پیام خود را بنویسید..."
              className="flex-1 border rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={connecting || sending}
            />
            <button
              type="submit"
              className={`bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md flex items-center gap-2 transition-colors ${
                (connecting || sending || !newMessage.trim()) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={connecting || sending || !newMessage.trim()}
            >
              {connecting ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>در حال اتصال...</span>
                </>
              ) : sending ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>در حال ارسال...</span>
                </>
              ) : (
                <>
                  <i className="fas fa-paper-plane"></i>
                  <span>ارسال</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatPage; 