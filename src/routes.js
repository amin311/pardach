import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// ایمپورت صفحات
import SetDesignPage from './pages/SetDesignPage';

// ایمپورت کامپوننت‌های لایه‌بندی
const DefaultLayout = React.lazy(() => import('./layouts/DefaultLayout'));
const AuthLayout = React.lazy(() => import('./layouts/AuthLayout'));

// ایمپورت صفحات موجود (احتمالی)
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const Register = React.lazy(() => import('./pages/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

const AppRoutes = () => {
  // این بخش می‌تواند بر اساس وضعیت احراز هویت تغییر کند
  const isAuthenticated = localStorage.getItem('token') !== null;

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