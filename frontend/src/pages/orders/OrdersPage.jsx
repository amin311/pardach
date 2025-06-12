import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  Add,
  Search,
  FilterList,
  MoreVert,
  Edit,
  Delete,
  Visibility,
  ShoppingCart,
  Schedule,
  CheckCircle,
  Cancel,
  Print,
  Download,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../../api/axiosInstance';

const OrdersPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || 'all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const orderStatuses = {
    pending: { label: 'در انتظار', color: 'warning', icon: <Schedule /> },
    processing: { label: 'در حال پردازش', color: 'info', icon: <ShoppingCart /> },
    completed: { label: 'تکمیل شده', color: 'success', icon: <CheckCircle /> },
    cancelled: { label: 'لغو شده', color: 'error', icon: <Cancel /> },
  };

  useEffect(() => {
    fetchOrders();
  }, [statusFilter, searchTerm, page, rowsPerPage]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      
      // فعلاً داده‌های نمونه استفاده می‌کنیم
      const mockOrders = [
        {
          id: 1,
          order_number: 'ORD-001',
          customer_name: 'شرکت ABC',
          total_amount: 1500000,
          status: 'pending',
          created_at: '2024-01-15T10:30:00Z',
          items_count: 3,
          description: 'سفارش چاپ کارت ویزیت',
        },
        {
          id: 2,
          order_number: 'ORD-002',
          customer_name: 'شرکت XYZ',
          total_amount: 2300000,
          status: 'processing',
          created_at: '2024-01-14T14:20:00Z',
          items_count: 5,
          description: 'سفارش چاپ بروشور',
        },
        {
          id: 3,
          order_number: 'ORD-003',
          customer_name: 'فروشگاه DEF',
          total_amount: 850000,
          status: 'completed',
          created_at: '2024-01-13T09:15:00Z',
          items_count: 2,
          description: 'سفارش چاپ پوستر',
        },
        {
          id: 4,
          order_number: 'ORD-004',
          customer_name: 'شرکت GHI',
          total_amount: 3200000,
          status: 'cancelled',
          created_at: '2024-01-12T16:45:00Z',
          items_count: 8,
          description: 'سفارش چاپ کاتالوگ',
        },
      ];

      // فیلتر کردن بر اساس وضعیت
      let filteredOrders = mockOrders;
      if (statusFilter !== 'all') {
        filteredOrders = mockOrders.filter(order => order.status === statusFilter);
      }

      // فیلتر کردن بر اساس جستجو
      if (searchTerm) {
        filteredOrders = filteredOrders.filter(order =>
          order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }

      setOrders(filteredOrders);
    } catch (error) {
      console.error('خطا در دریافت سفارشات:', error);
      toast.error('خطا در بارگذاری سفارشات');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event, order) => {
    setAnchorEl(event.currentTarget);
    setSelectedOrder(order);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedOrder(null);
  };

  const handleViewOrder = () => {
    navigate(`/orders/${selectedOrder.id}`);
    handleMenuClose();
  };

  const handleEditOrder = () => {
    navigate(`/orders/${selectedOrder.id}/edit`);
    handleMenuClose();
  };

  const handleDeleteOrder = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const confirmDelete = async () => {
    try {
      // await api.delete(`/api/orders/${selectedOrder.id}/`);
      toast.success('سفارش با موفقیت حذف شد');
      fetchOrders();
    } catch (error) {
      toast.error('خطا در حذف سفارش');
    }
    setDeleteDialogOpen(false);
    setSelectedOrder(null);
  };

  const handleStatusFilterChange = (status) => {
    setStatusFilter(status);
    setSearchParams(status === 'all' ? {} : { status });
    setPage(0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  const getStatusChip = (status) => {
    const statusInfo = orderStatuses[status];
    return (
      <Chip
        icon={statusInfo.icon}
        label={statusInfo.label}
        color={statusInfo.color}
        size="small"
        variant="outlined"
      />
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
            مدیریت سفارشات
          </Typography>
          <Typography variant="body2" color="text.secondary">
            مشاهده و مدیریت تمام سفارشات سیستم
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/orders/new')}
          sx={{ borderRadius: 2 }}
        >
          سفارش جدید
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {Object.entries(orderStatuses).map(([status, info]) => {
          const count = orders.filter(order => order.status === status).length;
          return (
            <Grid item xs={12} sm={6} md={3} key={status}>
              <Card
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: statusFilter === status ? 2 : 0,
                  borderColor: `${info.color}.main`,
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3,
                  },
                }}
                onClick={() => handleStatusFilterChange(status)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="textSecondary" gutterBottom variant="body2">
                        {info.label}
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {count}
                      </Typography>
                    </Box>
                    <Avatar sx={{ bgcolor: `${info.color}.light`, color: `${info.color}.main` }}>
                      {info.icon}
                    </Avatar>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="جستجو در سفارشات..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label="همه"
                  color={statusFilter === 'all' ? 'primary' : 'default'}
                  onClick={() => handleStatusFilterChange('all')}
                  clickable
                />
                {Object.entries(orderStatuses).map(([status, info]) => (
                  <Chip
                    key={status}
                    label={info.label}
                    color={statusFilter === status ? info.color : 'default'}
                    onClick={() => handleStatusFilterChange(status)}
                    clickable
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Orders Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>شماره سفارش</TableCell>
                <TableCell>مشتری</TableCell>
                <TableCell>توضیحات</TableCell>
                <TableCell>مبلغ</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>تاریخ ایجاد</TableCell>
                <TableCell align="center">عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {order.order_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{order.customer_name}</TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {order.description}
                      </Typography>
                    </TableCell>
                    <TableCell>{formatCurrency(order.total_amount)}</TableCell>
                    <TableCell>{getStatusChip(order.status)}</TableCell>
                    <TableCell>{formatDate(order.created_at)}</TableCell>
                    <TableCell align="center">
                      <IconButton
                        onClick={(e) => handleMenuOpen(e, order)}
                        size="small"
                      >
                        <MoreVert />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={orders.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          labelRowsPerPage="تعداد ردیف در صفحه:"
          labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} از ${count !== -1 ? count : `بیش از ${to}`}`
          }
        />
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewOrder}>
          <Visibility sx={{ mr: 1 }} />
          مشاهده جزئیات
        </MenuItem>
        <MenuItem onClick={handleEditOrder}>
          <Edit sx={{ mr: 1 }} />
          ویرایش
        </MenuItem>
        <MenuItem>
          <Print sx={{ mr: 1 }} />
          چاپ
        </MenuItem>
        <MenuItem>
          <Download sx={{ mr: 1 }} />
          دانلود
        </MenuItem>
        <MenuItem onClick={handleDeleteOrder} sx={{ color: 'error.main' }}>
          <Delete sx={{ mr: 1 }} />
          حذف
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>تأیید حذف</DialogTitle>
        <DialogContent>
          آیا از حذف سفارش {selectedOrder?.order_number} اطمینان دارید؟
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>انصراف</Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            حذف
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => navigate('/orders/new')}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default OrdersPage; 