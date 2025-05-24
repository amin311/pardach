import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TextField, Button, Typography, Box, 
  Alert, InputAdornment, IconButton 
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('لطفاً نام کاربری و رمز عبور را وارد کنید');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // در یک پروژه واقعی، این بخش با API ارتباط برقرار می‌کند
      // اینجا فقط شبیه‌سازی کرده‌ایم
      
      // شبیه‌سازی API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // شبیه‌سازی دریافت توکن از سرور
      const fakeToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake";
      
      // ذخیره توکن در localStorage
      localStorage.setItem('token', fakeToken);
      
      // هدایت به صفحه اصلی
      navigate('/');
    } catch (err) {
      setError('خطا در ورود به سیستم. لطفاً دوباره تلاش کنید.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Typography component="h1" variant="h5" sx={{ mb: 3, textAlign: 'center' }}>
        ورود به سیستم
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="username"
          label="نام کاربری"
          name="username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          sx={{ mb: 2 }}
        />
        <TextField
          margin="normal"
          required
          fullWidth
          name="password"
          label="رمز عبور"
          type={showPassword ? 'text' : 'password'}
          id="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            )
          }}
          sx={{ mb: 2 }}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? 'در حال پردازش...' : 'ورود'}
        </Button>
      </Box>
    </Box>
  );
};

export default Login; 