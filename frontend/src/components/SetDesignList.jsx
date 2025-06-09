import React, { useState, useEffect } from 'react';
import { 
  Paper, Typography, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Button, Box, Chip, CircularProgress
} from '@mui/material';
import axiosInstance from './lib/axios';

const statusColors = {
  waiting: 'warning',
  in_progress: 'info',
  pending_approval: 'secondary',
  rejected: 'error',
  completed: 'success'
};

const SetDesignList = () => {
  const [setDesigns, setSetDesigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSetDesigns();
  }, []);

  const fetchSetDesigns = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/set-design/set-design/');
      setSetDesigns(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching set designs:', err);
      setError('خطا در دریافت لیست ست‌بندی‌ها. لطفاً دوباره تلاش کنید.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await axiosInstance.post(`/api/set-design/set-design/${id}/approve/`, {
        approved: true
      });
      fetchSetDesigns(); // Refresh list
      alert('ست‌بندی با موفقیت تأیید شد.');
    } catch (err) {
      console.error('Error approving set design:', err);
      alert('خطا در تأیید ست‌بندی. لطفاً دوباره تلاش کنید.');
    }
  };

  const handleReject = async (id, comment) => {
    const userComment = prompt('لطفاً دلیل رد ست‌بندی را وارد کنید:');
    if (!userComment) return;
    
    try {
      await axiosInstance.post(`/api/set-design/set-design/${id}/approve/`, {
        approved: false,
        comment: userComment
      });
      fetchSetDesigns(); // Refresh list
      alert('ست‌بندی رد شد و بازخورد شما ثبت گردید.');
    } catch (err) {
      console.error('Error rejecting set design:', err);
      alert('خطا در رد ست‌بندی. لطفاً دوباره تلاش کنید.');
    }
  };

  const handlePay = async (id, price) => {
    try {
      await axiosInstance.post(`/api/set-design/set-design/${id}/pay/`, {
        payment_method: 'internal',
        amount: price
      });
      fetchSetDesigns(); // Refresh list
      alert('پرداخت با موفقیت انجام شد.');
    } catch (err) {
      console.error('Error paying for set design:', err);
      alert('خطا در پرداخت. لطفاً دوباره تلاش کنید.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, my: 2 }}>
        <Typography color="error">{error}</Typography>
        <Button onClick={fetchSetDesigns} variant="contained" sx={{ mt: 2 }}>
          تلاش مجدد
        </Button>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, my: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" component="h2">
          لیست ست‌بندی‌ها
        </Typography>
        <Button variant="outlined" onClick={fetchSetDesigns}>
          بروزرسانی
        </Button>
      </Box>

      {setDesigns.length === 0 ? (
        <Typography>هیچ ست‌بندی یافت نشد.</Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>شناسه</TableCell>
                <TableCell>نسخه</TableCell>
                <TableCell>ست‌بند</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>قیمت (ریال)</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {setDesigns.map((set) => (
                <TableRow key={set.id}>
                  <TableCell>{set.id.substring(0, 8)}...</TableCell>
                  <TableCell>{set.version}</TableCell>
                  <TableCell>{set.designer_name || 'تعیین نشده'}</TableCell>
                  <TableCell>
                    <Chip 
                      label={set.status_display} 
                      color={statusColors[set.status] || 'default'} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{set.price.toLocaleString()}</TableCell>
                  <TableCell>
                    {set.status === 'pending_approval' && (
                      <>
                        <Button 
                          size="small" 
                          variant="contained" 
                          color="success"
                          onClick={() => handleApprove(set.id)}
                          sx={{ mr: 1 }}
                        >
                          تأیید
                        </Button>
                        <Button 
                          size="small" 
                          variant="contained" 
                          color="error" 
                          onClick={() => handleReject(set.id)}
                        >
                          رد
                        </Button>
                      </>
                    )}
                    {set.status === 'completed' && !set.paid && (
                      <Button 
                        size="small" 
                        variant="contained" 
                        onClick={() => handlePay(set.id, set.price)}
                      >
                        پرداخت
                      </Button>
                    )}
                    {set.file && (
                      <Button 
                        size="small" 
                        href={set.file} 
                        target="_blank" 
                        sx={{ ml: 1 }}
                      >
                        دانلود فایل
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default SetDesignList; 