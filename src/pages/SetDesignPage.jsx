import React from 'react';
import { Container, Typography, Box, Breadcrumbs, Link } from '@mui/material';
import SetDesignList from '../components/SetDesignList';

const SetDesignPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ pt: 4, pb: 2 }}>
        <Breadcrumbs aria-label="breadcrumb">
          <Link underline="hover" color="inherit" href="/">
            داشبورد
          </Link>
          <Typography color="text.primary">ست‌بندی</Typography>
        </Breadcrumbs>
        
        <Typography variant="h4" component="h1" sx={{ mt: 2, mb: 4, fontWeight: 'bold' }}>
          مدیریت ست‌بندی‌ها
        </Typography>
        
        <SetDesignList />
      </Box>
    </Container>
  );
};

export default SetDesignPage; 