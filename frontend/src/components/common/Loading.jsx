import React from 'react';
import { Box, CircularProgress, Typography, Backdrop } from '@mui/material';

const Loading = ({ 
  message = 'در حال بارگذاری...', 
  backdrop = false, 
  size = 40,
  fullScreen = false 
}) => {
  const LoadingContent = () => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        ...(fullScreen && {
          minHeight: '100vh',
        }),
      }}
    >
      <CircularProgress size={size} />
      <Typography variant="body2" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );

  if (backdrop) {
    return (
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          flexDirection: 'column',
          gap: 2,
        }}
        open={true}
      >
        <CircularProgress color="inherit" size={size} />
        <Typography variant="body1" color="inherit">
          {message}
        </Typography>
      </Backdrop>
    );
  }

  return <LoadingContent />;
};

export default Loading; 