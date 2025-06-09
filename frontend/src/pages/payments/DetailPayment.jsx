import React, { useState, useEffect } from 'react';
import { 
  Box, Heading, Text, Spinner, Flex, Icon, Badge, 
  Grid, GridItem, Divider, Button, Alert, AlertIcon,
  Accordion, AccordionItem, AccordionButton, AccordionPanel, 
  AccordionIcon, useToast, Card, CardHeader, CardBody
} from '@chakra-ui/react';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { 
  FaMoneyBill, FaCheckCircle, FaTimesCircle, FaHourglassHalf, 
  FaBan, FaUser, FaShoppingCart, FaCalendarAlt, FaInfoCircle,
  FaExchangeAlt, FaArrowLeft, FaHistory, FaGlobe
} from 'react-icons/fa';
import axiosInstance from '../../lib/axios';
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

const DetailPayment = () => {
  const { id } = useParams();
  const [payment, setPayment] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.is_staff || user?.is_superuser;

  useEffect(() => {
    fetchPaymentDetails();
  }, [id]);

  const fetchPaymentDetails = async () => {
    try {
      setLoading(true);
      
      // دریافت اطلاعات پرداخت
      const paymentResponse = await axiosInstance.get(`/payment/payments/${id}/`);
      setPayment(paymentResponse.data);
      
      // دریافت تراکنش‌های مرتبط
      const transactionsResponse = await axiosInstance.get(`/payment/payments/${id}/transactions/`);
      setTransactions(transactionsResponse.data);
      
      setError(null);
    } catch (error) {
      console.error('خطا در دریافت جزئیات پرداخت:', error);
      setError('مشکلی در دریافت اطلاعات پرداخت وجود دارد');
      
      toast({
        title: 'خطا در دریافت اطلاعات',
        description: 'مشکلی در دریافت جزئیات پرداخت وجود دارد',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // تبدیل تاریخ به فرمت فارسی
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
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
    if (!amount) return '';
    
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  if (loading) {
    return (
      <Flex justify="center" align="center" minHeight="50vh">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error || !payment) {
    return (
      <Box p={5}>
        <Alert status="error" mb={5}>
          <AlertIcon />
          {error || 'پرداخت مورد نظر یافت نشد'}
        </Alert>
        <Button as={RouterLink} to="/payments" leftIcon={<FaArrowLeft />} colorScheme="blue">
          بازگشت به لیست پرداخت‌ها
        </Button>
      </Box>
    );
  }

  const statusInfo = getStatusInfo(payment.status);

  return (
    <Box p={5}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading as="h1" size="lg">
          <Flex align="center">
            <Icon as={FaMoneyBill} mr={2} />
            جزئیات پرداخت
          </Flex>
        </Heading>
        
        <Button 
          as={RouterLink} 
          to="/payments" 
          leftIcon={<FaArrowLeft />} 
          colorScheme="blue" 
          variant="outline"
        >
          بازگشت به لیست
        </Button>
      </Flex>

      <Card mb={6} variant="outline">
        <CardHeader bg="blue.50" py={3}>
          <Flex justify="space-between" align="center">
            <Heading size="md">
              <Flex align="center">
                <Icon as={FaInfoCircle} mr={2} />
                اطلاعات پرداخت
              </Flex>
            </Heading>
            <Badge 
              colorScheme={statusInfo.color} 
              fontSize="md" 
              px={3} 
              py={1} 
              borderRadius="md"
              display="flex"
              alignItems="center"
            >
              <Icon as={statusInfo.icon} mr={2} />
              {statusInfo.text}
            </Badge>
          </Flex>
        </CardHeader>
        
        <CardBody>
          <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
            <GridItem>
              <Flex mb={4}>
                <Icon as={FaUser} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">کاربر</Text>
                  <Text>{payment.user_display}</Text>
                </Box>
              </Flex>

              <Flex mb={4}>
                <Icon as={FaShoppingCart} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">کد سفارش</Text>
                  <Text>{payment.order_code || '-'}</Text>
                </Box>
              </Flex>

              <Flex mb={4}>
                <Icon as={FaMoneyBill} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">مبلغ</Text>
                  <Text fontWeight="bold">{formatMoney(payment.amount)}</Text>
                </Box>
              </Flex>
            </GridItem>

            <GridItem>
              <Flex mb={4}>
                <Icon as={FaExchangeAlt} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">شناسه تراکنش</Text>
                  <Text fontFamily="monospace">{payment.transaction_id}</Text>
                </Box>
              </Flex>

              <Flex mb={4}>
                <Icon as={FaGlobe} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">درگاه پرداخت</Text>
                  <Text>
                    {payment.gateway === 'zarinpal' && 'زرین‌پال'}
                    {payment.gateway === 'idpay' && 'آیدی‌پی'}
                    {payment.gateway === 'internal' && 'داخلی'}
                  </Text>
                </Box>
              </Flex>

              <Flex mb={4}>
                <Icon as={FaCalendarAlt} mr={3} color="blue.500" boxSize={5} />
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.500">تاریخ ایجاد</Text>
                  <Text>{payment.created_at_jalali || formatDate(payment.created_at)}</Text>
                </Box>
              </Flex>
            </GridItem>
          </Grid>

          {payment.description && (
            <>
              <Divider my={4} />
              <Text fontWeight="bold" mb={2}>توضیحات:</Text>
              <Text>{payment.description}</Text>
            </>
          )}
        </CardBody>
      </Card>

      {/* تراکنش‌ها */}
      <Card variant="outline">
        <CardHeader bg="green.50" py={3}>
          <Heading size="md">
            <Flex align="center">
              <Icon as={FaHistory} mr={2} />
              تاریخچه تراکنش‌ها
            </Flex>
          </Heading>
        </CardHeader>
        
        <CardBody>
          {transactions.length === 0 ? (
            <Text textAlign="center" py={4} color="gray.500">
              هیچ تراکنشی برای این پرداخت ثبت نشده است
            </Text>
          ) : (
            <Accordion allowToggle>
              {transactions.map((transaction, index) => {
                const txStatusInfo = getStatusInfo(transaction.status);
                
                return (
                  <AccordionItem key={transaction.id}>
                    <h2>
                      <AccordionButton>
                        <Box flex="1" textAlign="right">
                          <Flex justify="space-between">
                            <Text>
                              تراکنش شماره {index + 1} - {formatDate(transaction.created_at)}
                            </Text>
                            <Badge colorScheme={txStatusInfo.color}>
                              {txStatusInfo.text}
                            </Badge>
                          </Flex>
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                    </h2>
                    <AccordionPanel pb={4}>
                      <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={4}>
                        <GridItem>
                          <Text fontWeight="bold">شناسه مرجع:</Text>
                          <Text fontFamily="monospace">{transaction.authority || '-'}</Text>
                        </GridItem>
                        <GridItem>
                          <Text fontWeight="bold">کد پیگیری:</Text>
                          <Text fontFamily="monospace">{transaction.ref_id || '-'}</Text>
                        </GridItem>
                        <GridItem>
                          <Text fontWeight="bold">مبلغ:</Text>
                          <Text>{formatMoney(transaction.amount)}</Text>
                        </GridItem>
                        <GridItem>
                          <Text fontWeight="bold">تاریخ:</Text>
                          <Text>{transaction.created_at_jalali || formatDate(transaction.created_at)}</Text>
                        </GridItem>
                      </Grid>
                      
                      {transaction.gateway_response && (
                        <Box mt={4}>
                          <Text fontWeight="bold">پاسخ درگاه:</Text>
                          <Box 
                            p={2} 
                            bg="gray.50" 
                            borderRadius="md" 
                            mt={1}
                            fontFamily="monospace"
                            fontSize="sm"
                            overflowX="auto"
                          >
                            <pre>{JSON.stringify(transaction.gateway_response, null, 2)}</pre>
                          </Box>
                        </Box>
                      )}
                    </AccordionPanel>
                  </AccordionItem>
                );
              })}
            </Accordion>
          )}
        </CardBody>
      </Card>
    </Box>
  );
};

export default DetailPayment; 