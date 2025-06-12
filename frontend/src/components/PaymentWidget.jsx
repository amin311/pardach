import React, { useState, useEffect } from 'react';
import { Box, Text, Badge, VStack, Heading, Divider, Spinner, Flex, Icon } from '@chakra-ui/react';
import { FaMoneyCheckAlt, FaCheckCircle, FaTimesCircle, FaHourglassHalf, FaBan } from 'react-icons/fa';
import axiosInstance from '../api/axiosInstance';
import { toast } from 'react-toastify';

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

const PaymentWidget = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        setLoading(true);
        // دریافت ۵ پرداخت اخیر
        const response = await axiosInstance.get('/api/payment/user-payments/?limit=5');
        setPayments(response.data);
        setError(null);
      } catch (err) {
        console.error('خطا در دریافت پرداخت‌ها:', err);
        setError('خطا در دریافت پرداخت‌ها');
        toast.error('خطا در دریافت پرداخت‌های اخیر');
      } finally {
        setLoading(false);
      }
    };

    fetchPayments();
  }, []);

  // تبدیل تاریخ به فرمت فارسی
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  // نمایش مبلغ به فرمت پول
  const formatMoney = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  if (loading) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" shadow="md">
        <Heading size="md" mb={4}>
          <Flex align="center">
            <Icon as={FaMoneyCheckAlt} mr={2} color="blue.500" />
            پرداخت‌های اخیر
          </Flex>
        </Heading>
        <Flex justify="center" align="center" h="150px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" shadow="md">
        <Heading size="md" mb={4}>
          <Flex align="center">
            <Icon as={FaMoneyCheckAlt} mr={2} color="blue.500" />
            پرداخت‌های اخیر
          </Flex>
        </Heading>
        <Text color="red.500" textAlign="center">
          {error}
        </Text>
      </Box>
    );
  }

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" shadow="md">
      <Heading size="md" mb={4}>
        <Flex align="center">
          <Icon as={FaMoneyCheckAlt} mr={2} color="blue.500" />
          پرداخت‌های اخیر
        </Flex>
      </Heading>

      {payments.length === 0 ? (
        <Text textAlign="center" p={4} color="gray.500">
          هنوز پرداختی انجام نشده است
        </Text>
      ) : (
        <VStack spacing={2} align="stretch">
          {payments.map((payment) => {
            const statusInfo = getStatusInfo(payment.status);
            
            return (
              <Box key={payment.id} p={3} borderWidth="1px" borderRadius="md" _hover={{ bg: 'gray.50' }}>
                <Flex justify="space-between" align="center">
                  <Text fontWeight="bold">
                    سفارش: {payment.order_code}
                  </Text>
                  <Badge colorScheme={statusInfo.color} display="flex" alignItems="center">
                    <Icon as={statusInfo.icon} mr={1} /> {statusInfo.text}
                  </Badge>
                </Flex>
                
                <Flex justify="space-between" mt={2} fontSize="sm">
                  <Text color="gray.600">مبلغ: {formatMoney(payment.amount)}</Text>
                  <Text color="gray.500" fontSize="xs">
                    {payment.created_at_jalali || formatDate(payment.created_at)}
                  </Text>
                </Flex>
              </Box>
            );
          })}
        </VStack>
      )}
      
      <Divider my={3} />
      
      <Text textAlign="left" fontSize="sm" color="blue.500" cursor="pointer" _hover={{ textDecoration: 'underline' }}>
        مشاهده همه پرداخت‌ها
      </Text>
    </Box>
  );
};

export default PaymentWidget; 