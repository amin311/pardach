import React from 'react';

const TenderDashboard = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">داشبورد مناقصات</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* اینجا محتوای داشبورد اضافه خواهد شد */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">مناقصات فعال</h2>
          <p>لیست مناقصات فعال در اینجا نمایش داده خواهد شد</p>
        </div>
      </div>
    </div>
  );
};

export default TenderDashboard; 