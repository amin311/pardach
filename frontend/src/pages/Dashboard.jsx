import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Avatar,
  Chip,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp,
  ShoppingCart,
  Assignment,
  People,
  Notifications,
  MoreVert,
  CheckCircle,
  Schedule,
  Warning,
  Error,
  Add,
} from '@mui/icons-material';
import { useOutletContext, useNavigate } from 'react-router-dom';
import api from '../api/axiosInstance';
import { toast } from 'react-toastify';

const Dashboard = () => {
  const { user } = useOutletContext();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalOrders: 0,
    pendingOrders: 0,
    completedOrders: 0,
    totalRevenue: 0,
    activeProjects: 0,
    totalUsers: 0,
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // در اینجا می‌توانید API های مختلف را فراخوانی کنید
      // const [ordersRes, usersRes, activitiesRes] = await Promise.all([
      //   api.get('/api/orders/stats/'),
      //   api.get('/api/auth/users/'),
      //   api.get('/api/activities/recent/')
      // ]);
      
      // فعلاً داده‌های نمونه استفاده می‌کنیم
      setStats({
        totalOrders: 156,
        pendingOrders: 23,
        completedOrders: 133,
        totalRevenue: 2450000,
        activeProjects: 12,
        totalUsers: 45,
      });

      setRecentActivities([
        { id: 1, type: 'order', message: 'سفارش جدید از شرکت ABC', time: '۵ دقیقه پیش', status: 'new' },
        { id: 2, type: 'payment', message: 'پرداخت سفارش #1234 تکمیل شد', time: '۱۵ دقیقه پیش', status: 'success' },
        { id: 3, type: 'design', message: 'طراحی جدید آپلود شد', time: '۳۰ دقیقه پیش', status: 'info' },
        { id: 4, type: 'user', message: 'کاربر جدید ثبت‌نام کرد', time: '۱ ساعت پیش', status: 'info' },
      ]);
    } catch (error) {
      console.error('خطا در دریافت داده‌های داشبورد:', error);
      toast.error('خطا در بارگذاری داده‌های داشبورد');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, trend, onClick }) => (
    <Card 
      sx={{ 
        height: '100%', 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        } : {},
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color }}>
              {typeof value === 'number' && value > 1000 
                ? `${(value / 1000).toFixed(0)}K` 
                : value.toLocaleString('fa-IR')}
            </Typography>
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <TrendingUp sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  {trend}
                </Typography>
              </Box>
            )}
          </Box>
          <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main` }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  const getActivityIcon = (type) => {
    switch (type) {
      case 'order': return <ShoppingCart />;
      case 'payment': return <CheckCircle />;
      case 'design': return <Assignment />;
      case 'user': return <People />;
      default: return <Notifications />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'new': return 'primary';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>در حال بارگذاری داشبورد...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          داشبورد
        </Typography>
        <Typography variant="body1" color="text.secondary">
          خوش آمدید {user?.first_name || user?.username}، خلاصه‌ای از وضعیت سیستم را مشاهده کنید.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="کل سفارشات"
            value={stats.totalOrders}
            icon={<ShoppingCart />}
            color="primary"
            trend="+12% این ماه"
            onClick={() => navigate('/orders')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="سفارشات در انتظار"
            value={stats.pendingOrders}
            icon={<Schedule />}
            color="warning"
            onClick={() => navigate('/orders?status=pending')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="سفارشات تکمیل شده"
            value={stats.completedOrders}
            icon={<CheckCircle />}
            color="success"
            trend="+8% این ماه"
            onClick={() => navigate('/orders?status=completed')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="درآمد کل (تومان)"
            value={stats.totalRevenue}
            icon={<TrendingUp />}
            color="success"
            trend="+15% این ماه"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="پروژه‌های فعال"
            value={stats.activeProjects}
            icon={<Assignment />}
            color="info"
            onClick={() => navigate('/projects')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="کل کاربران"
            value={stats.totalUsers}
            icon={<People />}
            color="secondary"
            onClick={() => navigate('/users')}
          />
        </Grid>
      </Grid>

      {/* Recent Activities and Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                فعالیت‌های اخیر
              </Typography>
              <IconButton>
                <MoreVert />
              </IconButton>
            </Box>
            <List>
              {recentActivities.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemIcon>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: `${getStatusColor(activity.status)}.light` }}>
                        {getActivityIcon(activity.type)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.message}
                      secondary={activity.time}
                    />
                    <Chip 
                      label={activity.status === 'new' ? 'جدید' : activity.status === 'success' ? 'موفق' : 'اطلاع'}
                      color={getStatusColor(activity.status)}
                      size="small"
                    />
                  </ListItem>
                  {index < recentActivities.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
              عملیات سریع
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Add />}
                fullWidth
                onClick={() => navigate('/orders/new')}
              >
                سفارش جدید
              </Button>
              <Button
                variant="outlined"
                startIcon={<Assignment />}
                fullWidth
                onClick={() => navigate('/designs/new')}
              >
                طراحی جدید
              </Button>
              <Button
                variant="outlined"
                startIcon={<People />}
                fullWidth
                onClick={() => navigate('/users/new')}
              >
                کاربر جدید
              </Button>
              <Button
                variant="outlined"
                startIcon={<DashboardIcon />}
                fullWidth
                onClick={() => navigate('/reports')}
              >
                مشاهده گزارشات
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 