import React, { useState, useEffect } from 'react';
import { 
  Box, Heading, Text, Spinner, Flex, Icon, Alert, AlertIcon, 
  Button, VStack, Card, CardBody, Badge, useToast
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import { 
  FaCheckCircle, FaTimesCircle, FaExclamationTriangle, 
  FaArrowLeft, FaHome, FaShoppingCart, FaMoneyBill
} from 'react-icons/fa';
import axios from 'axios';

const PaymentCallback = () => {
  const [loading, setLoading] = useState(true);
  const [paymentResult, setPaymentResult] = useState(null);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    verifyPayment();
  }, [location.search]);

  const verifyPayment = async () => {
    try {
      setLoading(true);
      
      // استخراج پارامترهای URL بر اساس درگاه پرداخت
      const params = new URLSearchParams(location.search);
      
      // پارامترهای زرین‌پال
      const authority = params.get('Authority');
      const status = params.get('Status');
      
      // پارامترهای IDPay
      const idPayId = params.get('id');
      const idPayStatus = params.get('status');
      
      // اگر هیچ پارامتری نباشد، خطا نمایش داده می‌شود
      if (!authority && !idPayId) {
        setError('پارامترهای لازم برای بررسی پرداخت یافت نشد');
        setLoading(false);
        return;
      }
      
      // ارسال درخواست تایید پرداخت به سرور
      const response = await axios.post('/api/payment/verify/', {
        authority: authority || '',
        status: status || idPayStatus || '',
        id_pay_id: idPayId || ''
      });
      
      setPaymentResult(response.data);
      
      // نمایش پیام مناسب
      toast({
        title: response.data.success ? 'پرداخت موفق' : 'پرداخت ناموفق',
        description: response.data.message,
        status: response.data.success ? 'success' : 'error',
        duration: 5000,
        isClosable: true,
      });
      
    } catch (err) {
      console.error('خطا در تایید پرداخت:', err);
      setError(err.response?.data?.error || 'خطای سیستمی در بررسی وضعیت پرداخت');
      
      toast({
        title: 'خطا در بررسی پرداخت',
        description: err.response?.data?.error || 'مشکلی در بررسی وضعیت پرداخت وجود دارد',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // نمایش در حال بارگذاری
  if (loading) {
    return (
      <Box p={5} textAlign="center">
        <VStack spacing={8}>
          <Heading size="lg">در حال بررسی وضعیت پرداخت</Heading>
          <Text>لطفاً صبر کنید...</Text>
          <Spinner size="xl" thickness="4px" speed="0.65s" color="blue.500" />
        </VStack>
      </Box>
    );
  }

  // نمایش خطا
  if (error) {
    return (
      <Box p={5}>
        <Card mb={5} bg="red.50">
          <CardBody>
            <VStack spacing={4} align="center">
              <Icon as={FaExclamationTriangle} boxSize={14} color="red.500" />
              <Heading size="lg">خطا در بررسی پرداخت</Heading>
              <Text>{error}</Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Flex justify="center" gap={4}>
          <Button 
            as={RouterLink} 
            to="/payments" 
            leftIcon={<FaMoneyBill />} 
            colorScheme="blue" 
            variant="outline"
          >
            پرداخت‌های من
          </Button>
          <Button 
            as={RouterLink} 
            to="/" 
            leftIcon={<FaHome />} 
            colorScheme="gray"
          >
            صفحه اصلی
          </Button>
        </Flex>
      </Box>
    );
  }

  // نمایش نتیجه پرداخت
  return (
    <Box p={5}>
      <Card 
        mb={5} 
        bg={paymentResult?.success ? "green.50" : "red.50"}
        boxShadow="md"
      >
        <CardBody>
          <VStack spacing={6} align="center" p={4}>
            <Icon 
              as={paymentResult?.success ? FaCheckCircle : FaTimesCircle} 
              boxSize={16} 
              color={paymentResult?.success ? "green.500" : "red.500"} 
            />
            
            <Heading size="lg">
              {paymentResult?.success ? 'پرداخت با موفقیت انجام شد' : 'پرداخت ناموفق'}
            </Heading>
            
            <Text>{paymentResult?.message}</Text>
            
            {paymentResult?.ref_id && (
              <Badge 
                colorScheme="green" 
                p={2} 
                fontSize="md" 
                borderRadius="md"
              >
                کد پیگیری: {paymentResult.ref_id}
              </Badge>
            )}
          </VStack>
        </CardBody>
      </Card>
      
      <Flex justify="center" gap={4} flexWrap="wrap">
        {paymentResult?.order_id && (
          <Button 
            as={RouterLink} 
            to={`/orders/${paymentResult.order_id}`} 
            leftIcon={<FaShoppingCart />} 
            colorScheme="green"
          >
            مشاهده سفارش
          </Button>
        )}
        
        <Button 
          as={RouterLink} 
          to="/payments" 
          leftIcon={<FaMoneyBill />} 
          colorScheme="blue" 
          variant="outline"
        >
          پرداخت‌های من
        </Button>
        
        <Button 
          as={RouterLink} 
          to="/" 
          leftIcon={<FaHome />} 
          colorScheme="gray"
        >
          صفحه اصلی
        </Button>
      </Flex>
    </Box>
  );
};

export default PaymentCallback; 