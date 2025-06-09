import React, { useEffect, useState } from 'react';
import axiosInstance from './lib/axios';
import { useNavigate } from 'react-router-dom';

const Home = () => {
    const [homeData, setHomeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHomeData = async () => {
            try {
                const response = await axiosInstance.get('/api/public/home');
                setHomeData(response.data);
                setLoading(false);
            } catch (err) {
                setError('خطا در دریافت اطلاعات صفحه اصلی');
                setLoading(false);
            }
        };

        fetchHomeData();
    }, []);

    const renderBlock = (block) => {
        switch (block.type) {
            case 'catalog_link':
                return (
                    <div key={block.id} className="catalog-link-block">
                        <h2>{block.title}</h2>
                        <a href={block.config.url || '/catalog'} className="btn btn-primary">
                            مشاهده کاتالوگ
                        </a>
                    </div>
                );
            case 'order_form':
                return (
                    <div key={block.id} className="order-form-block">
                        <h2>{block.title}</h2>
                        {/* فرم سفارش را اینجا قرار دهید */}
                    </div>
                );
            case 'business_grid':
                return (
                    <div key={block.id} className="business-grid-block">
                        <h2>{block.title}</h2>
                        {/* گرید کسب‌وکارها را اینجا قرار دهید */}
                    </div>
                );
            case 'profile_short':
                return (
                    <div key={block.id} className="profile-shortcut-block">
                        <h2>{block.title}</h2>
                        <button onClick={() => navigate('/profile')} className="btn btn-secondary">
                            مشاهده پروفایل
                        </button>
                    </div>
                );
            case 'video_banner':
                return (
                    <div key={block.id} className="video-banner-block">
                        <h2>{block.title}</h2>
                        <video src={block.config.videoUrl} controls className="w-100" />
                    </div>
                );
            default:
                return null;
        }
    };

    if (loading) return <div className="text-center">در حال بارگذاری...</div>;
    if (error) return <div className="text-center text-danger">{error}</div>;
    if (!homeData) return null;

    return (
        <div className="home-page">
            {homeData.require_signup && (
                <div className="alert alert-info">
                    برای دسترسی به تمام امکانات، لطفاً ثبت‌نام کنید.
                </div>
            )}
            <div className="home-blocks">
                {homeData.blocks.map(renderBlock)}
            </div>
        </div>
    );
};

export default Home; 