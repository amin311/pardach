import { Link } from 'react-router-dom';

export function LandingLockScreen() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            به سایت ما خوش آمدید
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            برای دسترسی به محتوای سایت، لطفاً ثبت‌نام کنید یا وارد شوید
          </p>
        </div>
        
        <div className="mt-8 space-y-4">
          <Link
            to="/register"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            ثبت‌نام
          </Link>
          
          <Link
            to="/login"
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            ورود
          </Link>
        </div>
      </div>
    </div>
  );
} 