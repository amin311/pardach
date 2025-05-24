import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container, Box, Paper, Typography, CssBaseline } from '@mui/material';

const AuthLayout = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: '#f5f5f5',
        direction: 'rtl',
      }}
    >
      <CssBaseline />
      <Container maxWidth="sm" sx={{ mb: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mt: 8,
          }}
        >
          <Typography component="h1" variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
            سیستم مدیریت چاپخانه
          </Typography>
          <Paper
            elevation={3}
            sx={{
              p: 4,
              width: '100%',
              borderRadius: 2,
            }}
          >
            <Outlet />
          </Paper>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 4 }}>
            © {new Date().getFullYear()} تمام حقوق محفوظ است.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default AuthLayout; 