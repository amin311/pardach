import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  AccountCircle,
  Dashboard,
  Settings,
  Logout,
  Notifications,
  Business,
  Assignment,
  DesignServices,
  ShoppingCart,
  Analytics,
  Group,
  Payment,
  Workshop,
  MenuBook,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const Navigation = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      onLogout && onLogout();
      toast.success('با موفقیت خارج شدید');
      navigate('/auth/login');
    } catch (error) {
      toast.error('خطا در خروج از سیستم');
    }
    handleMenuClose();
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMenuClose();
  };

  const menuItems = [
    { icon: <Dashboard />, text: 'داشبورد', path: '/' },
    { icon: <DesignServices />, text: 'طراحی‌ها', path: '/designs' },
    { icon: <ShoppingCart />, text: 'سفارشات', path: '/orders' },
    { icon: <Assignment />, text: 'مناقصات', path: '/tenders' },
    { icon: <Business />, text: 'کسب و کارها', path: '/businesses' },
    { icon: <Workshop />, text: 'کارگاه', path: '/workshop' },
    { icon: <Analytics />, text: 'گزارشات', path: '/reports' },
    { icon: <Payment />, text: 'پرداخت‌ها', path: '/payments' },
    { icon: <Group />, text: 'کاربران', path: '/users' },
    { icon: <MenuBook />, text: 'قالب‌ها', path: '/templates' },
  ];

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ 
            flexGrow: 1, 
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
          onClick={() => navigate('/')}
        >
          سیستم پرداچ
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton color="inherit">
            <Notifications />
          </IconButton>

          <Button
            color="inherit"
            startIcon={<AccountCircle />}
            onClick={handleMenuOpen}
            sx={{ ml: 1 }}
          >
            {user?.first_name || user?.username || 'کاربر'}
          </Button>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 280,
                '& .MuiMenuItem-root': {
                  px: 2,
                  py: 1,
                },
              },
            }}
          >
            <MenuItem onClick={() => handleNavigation('/profile')}>
              <ListItemIcon>
                <Avatar sx={{ width: 24, height: 24 }}>
                  {(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
                </Avatar>
              </ListItemIcon>
              <ListItemText 
                primary={user?.first_name || user?.username || 'کاربر'}
                secondary={user?.email}
              />
            </MenuItem>

            <Divider />

            {menuItems.map((item, index) => (
              <MenuItem key={index} onClick={() => handleNavigation(item.path)}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </MenuItem>
            ))}

            <Divider />

            <MenuItem onClick={() => handleNavigation('/settings')}>
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText primary="تنظیمات" />
            </MenuItem>

            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout />
              </ListItemIcon>
              <ListItemText primary="خروج" />
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation; 