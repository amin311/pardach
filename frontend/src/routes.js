import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Loading from './components/common/Loading';

// ایمپورت صفحات
import SetDesignPage from './pages/SetDesignPage';
import Home from './pages/Home';
import TenderDashboard from './pages/TenderDashboard';

// ایمپورت کامپوننت‌های لایه‌بندی
const DefaultLayout = React.lazy(() => import('./layouts/DefaultLayout'));
const AuthLayout = React.lazy(() => import('./layouts/AuthLayout'));

// ایمپورت صفحات موجود
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const Register = React.lazy(() => import('./pages/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

// ایمپورت صفحات جدید
const ListUsers = React.lazy(() => import('./pages/auth/ListUsers'));
const OrdersPage = React.lazy(() => import('./pages/orders/OrdersPage'));

// صفحات اضافی که ممکن است نیاز باشد
const DesignsPage = React.lazy(() => import('./pages/designs/DesignsPage'));
const BusinessesPage = React.lazy(() => import('./pages/businesses/BusinessesPage'));
const WorkshopPage = React.lazy(() => import('./pages/WorkshopPage'));
const ReportsPage = React.lazy(() => import('./pages/reports/ReportsPage'));
const PaymentsPage = React.lazy(() => import('./pages/payments/PaymentsPage'));
const TemplatesPage = React.lazy(() => import('./pages/templates/TemplatesPage'));
const SettingsPage = React.lazy(() => import('./pages/SettingsPage'));
const ProfilePage = React.lazy(() => import('./pages/ProfilePage'));

// تنظیمات future flags
const router = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
};

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
    <BrowserRouter {...router}>
      <React.Suspense fallback={<Loading message="در حال بارگذاری..." fullScreen />}>
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
            <Route path="dashboard" element={<Dashboard />} />
            
            {/* مسیرهای اصلی سیستم */}
            <Route path="orders" element={<OrdersPage />} />
            <Route path="designs" element={<DesignsPage />} />
            <Route path="tenders" element={<TenderDashboard />} />
            <Route path="businesses" element={<BusinessesPage />} />
            <Route path="workshop" element={<WorkshopPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="payments" element={<PaymentsPage />} />
            <Route path="templates" element={<TemplatesPage />} />
            
            {/* مسیرهای کاربری */}
            <Route path="users" element={<ListUsers />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
            
            {/* مسیرهای قدیمی برای سازگاری */}
            <Route path="set-design" element={<SetDesignPage />} />
            <Route path="home" element={<Home />} />
          </Route>

          {/* صفحه ۴۰۴ */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </React.Suspense>
    </BrowserRouter>
  );
};

export default AppRoutes; 