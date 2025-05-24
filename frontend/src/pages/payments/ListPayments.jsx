import React, { useState, useEffect } from 'react';
import { 
  Box, Flex, Heading, Text, Button, Table, Thead, Tbody, Tr, Th, Td, 
  Badge, Spinner, Select, useToast, Icon, useDisclosure, 
  AlertDialog, AlertDialogOverlay, AlertDialogContent, 
  AlertDialogHeader, AlertDialogBody, AlertDialogFooter,
  Link
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { 
  FaEye, FaEdit, FaTrash, FaFilter, FaMoneyBill, 
  FaCheckCircle, FaTimesCircle, FaHourglassHalf, FaBan
} from 'react-icons/fa';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

// تبدیل وضعیت پرداخت به رنگ و آیکون
const getStatusInfo = (status) => {
  switch (status) {
    case 'successful':
      return { color: 'green', icon: FaCheckCircle, text: 'موفق' };
    case 'failed':
      return { color: 'red', icon: FaTimesCircle, text: 'ناموفق' };
    case 'pending':
      return { color: 'yellow', icon: FaHourglassHalf, text: 'در انتظار' };
    case 'cancelled':
      return { color: 'gray', icon: FaBan, text: 'لغو شده' };
    default:
      return { color: 'gray', icon: FaHourglassHalf, text: 'نامشخص' };
  }
};

const ListPayments = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedPayment, setSelectedPayment] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = React.useRef();
  const toast = useToast();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.is_staff || user?.is_superuser;

  useEffect(() => {
    fetchPayments();
  }, [statusFilter]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      let url = '/api/payment/payments/';
      if (statusFilter) {
        url += `?status=${statusFilter}`;
      }
      
      const response = await axios.get(url);
      setPayments(response.data);
    } catch (error) {
      console.error('خطا در دریافت پرداخت‌ها:', error);
      toast({
        title: 'خطا در دریافت اطلاعات',
        description: 'مشکلی در دریافت لیست پرداخت‌ها وجود دارد',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (payment) => {
    setSelectedPayment(payment);
    onOpen();
  };

  const confirmDelete = async () => {
    if (!selectedPayment) return;
    
    try {
      await axios.delete(`/api/payment/payments/${selectedPayment.id}/`);
      
      // بروزرسانی لیست پس از حذف
      setPayments(payments.filter(p => p.id !== selectedPayment.id));
      
      toast({
        title: 'پرداخت حذف شد',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('خطا در حذف پرداخت:', error);
      toast({
        title: 'خطا در حذف پرداخت',
        description: error.response?.data?.detail || 'مشکلی در حذف پرداخت وجود دارد',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      onClose();
      setSelectedPayment(null);
    }
  };

  // تبدیل تاریخ به فرمت فارسی
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  };

  // نمایش مبلغ به فرمت پول
  const formatMoney = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  // بررسی دسترسی برای حذف و ویرایش
  const canEditOrDelete = (payment) => {
    // اگر کاربر ادمین است یا پرداخت متعلق به خودش است و در وضعیت در انتظار است
    return isAdmin || (payment.user === user?.id && payment.status === 'pending');
  };

  return (
    <Box p={4}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading as="h1" size="lg">
          <Flex align="center">
            <Icon as={FaMoneyBill} mr={2} />
            مدیریت پرداخت‌ها
          </Flex>
        </Heading>
        
        <Flex>
          {/* فیلتر وضعیت */}
          <Flex align="center" mr={4}>
            <Icon as={FaFilter} mr={2} />
            <Select 
              placeholder="فیلتر بر اساس وضعیت" 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              size="sm"
              width="200px"
            >
              <option value="">همه</option>
              <option value="pending">در انتظار</option>
              <option value="successful">موفق</option>
              <option value="failed">ناموفق</option>
              <option value="cancelled">لغو شده</option>
            </Select>
          </Flex>
        </Flex>
      </Flex>

      {loading ? (
        <Flex justify="center" my={10}>
          <Spinner size="xl" />
        </Flex>
      ) : payments.length === 0 ? (
        <Box textAlign="center" my={10}>
          <Text fontSize="lg" mb={4}>هیچ پرداختی یافت نشد</Text>
          {statusFilter && (
            <Text fontSize="sm" color="gray.500">
              فیلتر فعلی: {statusFilter}
            </Text>
          )}
        </Box>
      ) : (
        <Box overflowX="auto">
          <Table variant="simple">
            <Thead bg="gray.100">
              <Tr>
                <Th>کد سفارش</Th>
                <Th>کاربر</Th>
                <Th>مبلغ</Th>
                <Th>وضعیت</Th>
                <Th>درگاه</Th>
                <Th>تاریخ</Th>
                <Th>عملیات</Th>
              </Tr>
            </Thead>
            <Tbody>
              {payments.map((payment) => {
                const statusInfo = getStatusInfo(payment.status);
                
                return (
                  <Tr key={payment.id}>
                    <Td>
                      {payment.order_code || '-'}
                    </Td>
                    <Td>{payment.user_display}</Td>
                    <Td>{formatMoney(payment.amount)}</Td>
                    <Td>
                      <Badge colorScheme={statusInfo.color} display="flex" alignItems="center" width="fit-content">
                        <Icon as={statusInfo.icon} mr={1} /> {statusInfo.text}
                      </Badge>
                    </Td>
                    <Td>
                      {payment.gateway === 'zarinpal' && 'زرین‌پال'}
                      {payment.gateway === 'idpay' && 'آیدی‌پی'}
                      {payment.gateway === 'internal' && 'داخلی'}
                    </Td>
                    <Td>{payment.created_at_jalali || formatDate(payment.created_at)}</Td>
                    <Td>
                      <Flex>
                        <Link as={RouterLink} to={`/payments/${payment.id}`}>
                          <Button size="sm" colorScheme="blue" variant="ghost" mr={2}>
                            <Icon as={FaEye} />
                          </Button>
                        </Link>
                        
                        {canEditOrDelete(payment) && (
                          <>
                            <Link as={RouterLink} to={`/payments/${payment.id}/edit`}>
                              <Button size="sm" colorScheme="green" variant="ghost" mr={2}>
                                <Icon as={FaEdit} />
                              </Button>
                            </Link>
                            
                            <Button 
                              size="sm" 
                              colorScheme="red" 
                              variant="ghost"
                              onClick={() => handleDelete(payment)}
                            >
                              <Icon as={FaTrash} />
                            </Button>
                          </>
                        )}
                      </Flex>
                    </Td>
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* دیالوگ تایید حذف */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              حذف پرداخت
            </AlertDialogHeader>

            <AlertDialogBody>
              آیا از حذف این پرداخت اطمینان دارید؟ این عمل قابل بازگشت نیست.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                انصراف
              </Button>
              <Button colorScheme="red" onClick={confirmDelete} mr={3}>
                حذف
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default ListPayments; 