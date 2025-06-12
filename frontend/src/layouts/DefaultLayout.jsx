import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, CircularProgress, Container } from '@mui/material';
import Navigation from '../components/common/Navigation';
import api from '../api/axiosInstance';
import { toast } from 'react-toastify';

const DefaultLayout = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // فرض می‌کنیم که endpoint برای گرفتن اطلاعات کاربر وجود دارد
        const response = await api.get('/api/auth/user/');
        setUser(response.data);
      } catch (error) {
        console.error('خطا در دریافت اطلاعات کاربر:', error);
        // اگر خطای احراز هویت باشد، کاربر به صفحه لاگین هدایت می‌شود
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/auth/login';
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleLogout = () => {
    setUser(null);
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <CircularProgress size={40} />
        <Box sx={{ color: 'text.secondary' }}>در حال بارگذاری...</Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navigation user={user} onLogout={handleLogout} />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default',
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            flex: 1,
            py: 3,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Outlet context={{ user, setUser }} />
        </Container>
      </Box>
    </Box>
  );
};

export default DefaultLayout; 