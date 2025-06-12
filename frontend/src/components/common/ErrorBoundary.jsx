import React from 'react';
import { Box, Typography, Button, Alert, Container } from '@mui/material';
import { ErrorOutline, Refresh } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // به‌روزرسانی state تا UI خطا نشان داده شود
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // می‌توانید خطا را به سرویس گزارش خطا ارسال کنید
    console.error('خطای غیرمنتظره در اپلیکیشن:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleReload = () => {
    window.location.reload();
  }

  handleGoHome = () => {
    window.location.href = '/';
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container maxWidth="md" sx={{ mt: 8 }}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              gap: 3
            }}
          >
            <ErrorOutline sx={{ fontSize: 80, color: 'error.main' }} />
            
            <Typography variant="h4" gutterBottom>
              خطایی رخ داده است
            </Typography>
            
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
              متأسفانه خطای غیرمنتظره‌ای در برنامه رخ داده است. لطفاً صفحه را بارگذاری مجدد کنید یا به صفحه اصلی بازگردید.
            </Typography>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Alert severity="error" sx={{ width: '100%', textAlign: 'left' }}>
                <Typography variant="body2" component="pre" sx={{ fontSize: '0.875rem' }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </Typography>
              </Alert>
            )}

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleReload}
              >
                بارگذاری مجدد
              </Button>
              
              <Button
                variant="outlined"
                onClick={this.handleGoHome}
              >
                بازگشت به خانه
              </Button>
            </Box>
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 