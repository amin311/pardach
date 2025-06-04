import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  IconButton
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

const RejectDialog = ({
  open,
  onClose,
  onConfirm,
  title = 'رد طرح',
  message = 'لطفاً دلیل رد طرح را وارد کنید:',
  confirmText = 'رد طرح',
  cancelText = 'لغو',
  loading = false,
  required = true
}) => {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  const handleConfirm = () => {
    if (required && !reason.trim()) {
      setError('وارد کردن دلیل الزامی است');
      return;
    }
    onConfirm(reason.trim());
  };

  const handleClose = () => {
    setReason('');
    setError('');
    onClose();
  };

  const handleReasonChange = (e) => {
    setReason(e.target.value);
    if (error) {
      setError('');
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <span style={{ fontSize: '1.5rem' }}>❌</span>
            <Typography variant="h6" component="span">
              {title}
            </Typography>
          </Box>
          <IconButton
            onClick={handleClose}
            size="small"
            sx={{ color: 'grey.500' }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 1 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {message}
        </Typography>
        
        <TextField
          fullWidth
          multiline
          rows={4}
          value={reason}
          onChange={handleReasonChange}
          placeholder="دلیل رد طرح را بنویسید..."
          error={!!error}
          helperText={error}
          disabled={loading}
          sx={{ mt: 1 }}
        />
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          color="inherit"
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="error"
          disabled={loading || (required && !reason.trim())}
          sx={{ minWidth: 100 }}
        >
          {loading ? 'در حال انجام...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RejectDialog; 