import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
          py: 8,
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 100, color: 'warning.main', mb: 3 }} />
        
        <Typography variant="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
          404
        </Typography>
        
        <Typography variant="h4" sx={{ mb: 4 }}>
          صفحه مورد نظر پیدا نشد!
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
          متأسفانه صفحه‌ای که به دنبال آن هستید وجود ندارد یا حذف شده است.
          می‌توانید به صفحه اصلی بازگردید.
        </Typography>
        
        <Button
          component={Link}
          to="/"
          variant="contained"
          size="large"
          sx={{ borderRadius: 2 }}
        >
          بازگشت به صفحه اصلی
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 