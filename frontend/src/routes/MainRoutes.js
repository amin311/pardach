import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import MainPage from '../pages/main/MainPage';
import CombinedDashboardComponent from '../components/CombinedDashboardComponent';
import PrivateRoute from '../components/auth/PrivateRoute';

// تعریف مسیرهای اصلی برنامه
const MainRoutes = () => {
  return (
    <Routes>
      {/* مسیر پیش‌فرض به صفحه اصلی */}
      <Route path="/" element={<Navigate to="/main" replace />} />
      
      {/* صفحه اصلی (نیاز به احراز هویت دارد) */}
      <Route 
        path="/main" 
        element={
          <PrivateRoute>
            <MainPage />
          </PrivateRoute>
        } 
      />
      
      {/* صفحه داشبورد یکپارچه (نیاز به احراز هویت دارد) */}
      <Route 
        path="/dashboard/combined" 
        element={
          <PrivateRoute>
            <CombinedDashboardComponent />
          </PrivateRoute>
        } 
      />
      
      {/* مسیر‌های دیگر برنامه */}
      
    </Routes>
  );
};

export default MainRoutes; 