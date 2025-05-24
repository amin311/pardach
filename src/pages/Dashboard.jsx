import React from 'react';
import { Typography, Grid, Paper, Box, Button } from '@mui/material';
import DesignServicesIcon from '@mui/icons-material/DesignServices';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PeopleIcon from '@mui/icons-material/People';
import { Link } from 'react-router-dom';

// کامپوننت کارت برای نمایش آمار
const StatCard = ({ title, value, icon, color }) => (
  <Paper 
    elevation={2}
    sx={{ 
      p: 3, 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      borderTop: `4px solid ${color}`,
    }}
  >
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
      <Typography variant="h6" component="h2" color="text.secondary">
        {title}
      </Typography>
      <Box sx={{ 
        bgcolor: color + '22',  // رنگ با شفافیت کم
        borderRadius: '50%',
        p: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {React.cloneElement(icon, { style: { color: color } })}
      </Box>
    </Box>
    <Typography variant="h4" component="p" sx={{ fontWeight: 'bold', mb: 2 }}>
      {value}
    </Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mt: 'auto' }}>
      به‌روزرسانی: امروز
    </Typography>
  </Paper>
);

// کامپوننت کارت برای نمایش لینک‌های دسترسی سریع
const QuickLinkCard = ({ title, description, path, icon, color }) => (
  <Paper 
    elevation={2}
    sx={{ 
      p: 3,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      transition: 'transform 0.2s',
      '&:hover': {
        transform: 'translateY(-5px)',
        boxShadow: 3
      }
    }}
  >
    <Box sx={{ 
      bgcolor: color + '22',
      borderRadius: '50%',
      p: 1,
      width: 'fit-content',
      display: 'flex',
      mb: 2
    }}>
      {React.cloneElement(icon, { style: { color: color } })}
    </Box>
    <Typography variant="h6" component="h2" sx={{ mb: 1 }}>
      {title}
    </Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      {description}
    </Typography>
    <Button 
      component={Link}
      to={path}
      variant="contained"
      sx={{ 
        mt: 'auto',
        bgcolor: color,
        '&:hover': {
          bgcolor: color + 'DD'
        }
      }}
    >
      مشاهده
    </Button>
  </Paper>
);

const Dashboard = () => {
  // در یک پروژه واقعی، این داده‌ها از API دریافت می‌شوند
  const stats = {
    pendingOrders: 12,
    pendingSets: 5,
    activeDesigners: 8
  };

  return (
    <Box sx={{ pt: 2 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 4, fontWeight: 'bold' }}>
        داشبورد
      </Typography>
      
      {/* کارت‌های آمار */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <StatCard 
            title="سفارش‌های در انتظار" 
            value={stats.pendingOrders} 
            icon={<ShoppingCartIcon />}
            color="#2196F3"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard 
            title="ست‌های در حال پردازش" 
            value={stats.pendingSets} 
            icon={<DesignServicesIcon />}
            color="#FF9800"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard 
            title="ست‌بندان فعال" 
            value={stats.activeDesigners} 
            icon={<PeopleIcon />}
            color="#4CAF50"
          />
        </Grid>
      </Grid>
      
      {/* لینک‌های دسترسی سریع */}
      <Typography variant="h5" component="h2" sx={{ mb: 3, mt: 4 }}>
        دسترسی سریع
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <QuickLinkCard 
            title="مدیریت ست‌بندی‌ها" 
            description="مشاهده، تأیید و پرداخت ست‌بندی‌های سفارش‌ها"
            path="/set-design"
            icon={<DesignServicesIcon />}
            color="#FF9800"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <QuickLinkCard 
            title="سفارش‌ها" 
            description="مدیریت سفارش‌ها، پیگیری وضعیت و ویرایش"
            path="/orders"
            icon={<ShoppingCartIcon />}
            color="#2196F3"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <QuickLinkCard 
            title="کاربران" 
            description="مدیریت کاربران، ست‌بندان و دسترسی‌ها"
            path="/users"
            icon={<PeopleIcon />}
            color="#4CAF50"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 