import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// ایمپورت صفحات
import SetDesignPage from './pages/SetDesignPage';
import Home from './pages/Home';
import TenderDashboard from './pages/TenderDashboard';

// ایمپورت کامپوننت‌های لایه‌بندی
const DefaultLayout = React.lazy(() => import('./layouts/DefaultLayout'));
const AuthLayout = React.lazy(() => import('./layouts/AuthLayout'));

// ایمپورت صفحات موجود (احتمالی)
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const Register = React.lazy(() => import('./pages/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

// ایمپورت صفحات جدید
const ListUsers = React.lazy(() => import('./pages/auth/ListUsers'));
const OrdersPage = React.lazy(() => import('./pages/orders/OrdersPage'));

const AppRoutes = () => {
  // بررسی وجود token معتبر
  const checkAuth = () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!accessToken || !refreshToken) {
      return false;
    }
    
    try {
      // بررسی انقضای token (اختیاری)
      const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      // اگر access token منقضی شده، اما refresh token موجود است
      if (tokenPayload.exp < currentTime && refreshToken) {
        return true; // axios interceptor خودش refresh می‌کند
      }
      
      return tokenPayload.exp > currentTime;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  };

  const isAuthenticated = checkAuth();

  return (
    <BrowserRouter>
      <React.Suspense fallback={<div>در حال بارگذاری...</div>}>
        <Routes>
          {/* مسیرهای عمومی */}
          <Route path="/auth" element={<AuthLayout />}>
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            <Route index element={<Navigate to="/auth/login" replace />} />
          </Route>

          {/* مسیرهای خصوصی */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <DefaultLayout />
              ) : (
                <Navigate to="/auth/login" replace />
              )
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="set-design" element={<SetDesignPage />} />
            <Route path="home" element={<Home />} />
            <Route path="tenders" element={<TenderDashboard />} />
            <Route path="users" element={<ListUsers />} />
            <Route path="orders" element={<OrdersPage />} />
            {/* سایر مسیرها */}
          </Route>

          {/* صفحه ۴۰۴ */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </React.Suspense>
    </BrowserRouter>
  );
};

export default AppRoutes; 