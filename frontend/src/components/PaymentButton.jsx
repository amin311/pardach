import React, { useState } from 'react';
import {
  Button,
  Icon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Select,
  Spinner,
  Text,
  Alert,
  AlertIcon,
  useToast,
  VStack,
  Flex,
  Box,
  Badge,
} from '@chakra-ui/react';
import { FaCreditCard, FaExternalLinkAlt, FaCheckCircle } from 'react-icons/fa';
import axiosInstance from '../api/axiosInstance';

const PaymentButton = ({ 
  orderId, 
  orderAmount,
  orderCode,
  buttonText = 'پرداخت',
  buttonSize = 'md',
  buttonVariant = 'solid',
  buttonColorScheme = 'green',
  onSuccess = () => {},
  isDisabled = false,
  alreadyPaid = false,
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [gateway, setGateway] = useState('zarinpal');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentUrl, setPaymentUrl] = useState(null);
  const toast = useToast();

  const handlePaymentRequest = async () => {
    if (!orderId) {
      setError('شناسه سفارش مشخص نشده است');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // ایجاد کالبک مناسب برای بازگشت از درگاه پرداخت
      const callbackUrl = `${window.location.origin}/payment/callback`;
      
      // درخواست پرداخت
      const response = await axiosInstance.post('/api/payment/request/', {
        order_id: orderId,
        gateway: gateway,
        callback_url: callbackUrl,
        description: `پرداخت سفارش ${orderCode || orderId}`
      });

      if (response.data.success) {
        // ذخیره URL پرداخت برای هدایت کاربر
        setPaymentUrl(response.data.payment_url);
        
        toast({
          title: 'درخواست پرداخت ثبت شد',
          description: 'درخواست پرداخت با موفقیت ثبت شد. لطفا برای ادامه به درگاه پرداخت هدایت شوید.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        setError(response.data.message || 'خطا در ایجاد درخواست پرداخت');
      }
    } catch (err) {
      console.error('خطا در درخواست پرداخت:', err);
      setError(err.response?.data?.error || 'خطا در اتصال به سرور');
      
      toast({
        title: 'خطا در ثبت درخواست',
        description: err.response?.data?.error || 'مشکلی در ثبت درخواست پرداخت وجود دارد',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const redirectToPayment = () => {
    if (paymentUrl) {
      window.location.href = paymentUrl;
    }
  };

  const resetModal = () => {
    setGateway('zarinpal');
    setError(null);
    setPaymentUrl(null);
    onClose();
  };

  return (
    <>
      <Button
        onClick={onOpen}
        leftIcon={<Icon as={FaCreditCard} />}
        colorScheme={buttonColorScheme}
        size={buttonSize}
        variant={buttonVariant}
        isDisabled={isDisabled || alreadyPaid}
      >
        {alreadyPaid ? (
          <Flex align="center">
            <Icon as={FaCheckCircle} mr={2} />
            پرداخت شده
          </Flex>
        ) : (
          buttonText
        )}
      </Button>

      <Modal isOpen={isOpen} onClose={resetModal} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <Flex align="center">
              <Icon as={FaCreditCard} mr={2} />
              پرداخت سفارش
            </Flex>
          </ModalHeader>
          <ModalCloseButton />

          <ModalBody>
            {paymentUrl ? (
              <VStack spacing={4} align="stretch">
                <Alert status="success">
                  <AlertIcon />
                  درخواست پرداخت با موفقیت ایجاد شد. برای ادامه به درگاه پرداخت منتقل شوید.
                </Alert>
                
                <Flex justify="center" mt={2}>
                  <Button
                    colorScheme="blue"
                    leftIcon={<FaExternalLinkAlt />}
                    onClick={redirectToPayment}
                  >
                    انتقال به درگاه پرداخت
                  </Button>
                </Flex>
              </VStack>
            ) : (
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontWeight="bold" mb={2}>
                    اطلاعات سفارش:
                  </Text>
                  
                  <Flex justify="space-between" align="center" bg="gray.50" p={3} borderRadius="md">
                    <Text>مبلغ قابل پرداخت:</Text>
                    <Badge colorScheme="green" p={2} fontSize="md">
                      {new Intl.NumberFormat('fa-IR').format(orderAmount)} تومان
                    </Badge>
                  </Flex>
                  
                  {orderCode && (
                    <Flex justify="space-between" align="center" mt={2}>
                      <Text>کد سفارش:</Text>
                      <Text fontWeight="bold">{orderCode}</Text>
                    </Flex>
                  )}
                </Box>

                <FormControl>
                  <FormLabel>انتخاب درگاه پرداخت</FormLabel>
                  <Select 
                    value={gateway} 
                    onChange={(e) => setGateway(e.target.value)}
                    disabled={loading}
                  >
                    <option value="zarinpal">زرین‌پال</option>
                    <option value="idpay">آیدی پی</option>
                    <option value="internal">پرداخت داخلی (تست)</option>
                  </Select>
                </FormControl>

                {error && (
                  <Alert status="error">
                    <AlertIcon />
                    {error}
                  </Alert>
                )}
              </VStack>
            )}
          </ModalBody>

          <ModalFooter>
            {!paymentUrl && (
              <>
                <Button colorScheme="gray" mr={3} onClick={resetModal} disabled={loading}>
                  انصراف
                </Button>
                <Button 
                  colorScheme="green" 
                  onClick={handlePaymentRequest} 
                  isLoading={loading}
                  loadingText="در حال پردازش"
                  leftIcon={!loading && <FaCreditCard />}
                >
                  پرداخت
                </Button>
              </>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default PaymentButton; 