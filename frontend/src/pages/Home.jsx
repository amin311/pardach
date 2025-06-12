import React, { useEffect, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const Home = () => {
    const [homeData, setHomeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHomeData = async () => {
            try {
                const response = await axiosInstance.get('/api/main/page-summary/', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
                });
                setHomeData(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching home data:', err);
                setError('خطا در دریافت اطلاعات صفحه اصلی');
                toast.error('خطا در دریافت اطلاعات صفحه اصلی');
                setLoading(false);
            }
        };

        fetchHomeData();
    }, []);

    const renderPromotionCard = (promotion, index) => {
        return (
            <div key={index} className="col-md-4 mb-3">
                <div className="card h-100">
                    {promotion.image && (
                        <img src={promotion.image} className="card-img-top" alt={promotion.title} />
                    )}
                    <div className="card-body">
                        <h5 className="card-title">{promotion.title}</h5>
                        <p className="card-text">{promotion.description}</p>
                        {promotion.link && (
                            <a href={promotion.link} className="btn btn-primary">
                                مشاهده
                            </a>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    const renderNavigationItem = (navItem, index) => {
        if (!navItem.visible) return null;
        
        return (
            <div key={index} className="col-md-3 mb-3">
                <div className="card text-center">
                    <div className="card-body">
                        <i className={`fas ${navItem.icon} fa-2x mb-2 text-primary`}></i>
                        <h6 className="card-title">{navItem.title}</h6>
                        <button 
                            onClick={() => navigate(navItem.link)} 
                            className="btn btn-outline-primary btn-sm"
                        >
                            ورود
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const renderSummaryCard = (title, count, icon, bgColor = 'primary') => {
        return (
            <div className="col-md-3 mb-3">
                <div className={`card bg-${bgColor} text-white`}>
                    <div className="card-body text-center">
                        <i className={`fas ${icon} fa-2x mb-2`}></i>
                        <h4>{count}</h4>
                        <p className="mb-0">{title}</p>
                    </div>
                </div>
            </div>
        );
    };

    if (loading) return <div className="text-center">در حال بارگذاری...</div>;
    if (error) return <div className="text-center text-danger">{error}</div>;
    if (!homeData) return null;

    const { summary, promotions, navigation, welcome_data } = homeData;

    return (
        <div className="home-page container-fluid p-4">
            {/* بخش خوش‌آمدگویی */}
            {welcome_data && (
                <div className="row mb-4">
                    <div className="col-12">
                        <div className="card bg-light">
                            <div className="card-body">
                                <h3 className="card-title">
                                    خوش آمدید، {welcome_data.full_name}!
                                </h3>
                                <p className="card-text">
                                    امروز: {welcome_data.today_date_jalali}
                                </p>
                                {welcome_data.unread_count > 0 && (
                                    <div className="alert alert-warning">
                                        شما {welcome_data.unread_count} اعلان خوانده نشده دارید
                                    </div>
                                )}
                                {welcome_data.order_in_progress > 0 && (
                                    <div className="alert alert-info">
                                        {welcome_data.order_in_progress} سفارش در حال پردازش دارید
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* خلاصه آمار */}
            {summary && (
                <div className="row mb-4">
                    <div className="col-12">
                        <h4 className="mb-3">خلاصه آمار</h4>
                    </div>
                    {renderSummaryCard('سفارش‌ها', summary.order_count, 'fa-shopping-cart', 'primary')}
                    {renderSummaryCard('پرداخت‌ها', summary.payment_count, 'fa-credit-card', 'success')}
                    {renderSummaryCard('اعلانات خوانده نشده', summary.unread_notifications, 'fa-bell', 'warning')}
                    {renderSummaryCard('طرح‌های اخیر', summary.recent_designs?.length || 0, 'fa-paint-brush', 'info')}
                </div>
            )}

            {/* تبلیغات */}
            {promotions && promotions.length > 0 && (
                <div className="row mb-4">
                    <div className="col-12">
                        <h4 className="mb-3">پیشنهادهای ویژه</h4>
                    </div>
                    {promotions.map(renderPromotionCard)}
                </div>
            )}

            {/* منوی ناوبری */}
            {navigation && navigation.length > 0 && (
                <div className="row mb-4">
                    <div className="col-12">
                        <h4 className="mb-3">دسترسی سریع</h4>
                    </div>
                    {navigation.map(renderNavigationItem)}
                </div>
            )}

            {/* فعالیت‌های اخیر */}
            {summary && summary.recent_orders && summary.recent_orders.length > 0 && (
                <div className="row">
                    <div className="col-12">
                        <h4 className="mb-3">سفارش‌های اخیر</h4>
                        <div className="table-responsive">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>شماره سفارش</th>
                                        <th>مبلغ</th>
                                        <th>وضعیت</th>
                                        <th>تاریخ</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {summary.recent_orders.map((order, index) => (
                                        <tr key={index}>
                                            <td>#{order.id}</td>
                                            <td>{order.total_price?.toLocaleString()} تومان</td>
                                            <td>
                                                <span className={`badge bg-${order.status === 'completed' ? 'success' : 'warning'}`}>
                                                    {order.status}
                                                </span>
                                            </td>
                                            <td>{order.created_at}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Home; 