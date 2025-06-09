from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from .models import Tag, DesignCategory, Family, Design, FamilyDesignRequirement, DesignFamily, PrintLocation
from .serializers import (
    TagSerializer, DesignCategorySerializer, FamilySerializer,
    DesignSerializer, FamilyDesignRequirementSerializer, DesignFamilySerializer,
    PrintLocationSerializer
)
from drf_spectacular.utils import extend_schema
from apps.core.utils import log_error, validate_file_size, validate_file_format
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action

# Create your views here.

class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List or create tags", responses={200: TagSerializer(many=True)})
    def get(self, request):
        try:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving tags", e)
            return Response({'error': 'خطا در دریافت برچسب‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Create a new tag", request=TagSerializer, responses={201: TagSerializer})
    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            serializer = TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating tag", e)
            return Response({'error': 'خطا در ایجاد برچسب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DesignCategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List or create design categories", responses={200: DesignCategorySerializer(many=True)})
    def get(self, request):
        try:
            categories = DesignCategory.objects.all()
            serializer = DesignCategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving design categories", e)
            return Response({'error': 'خطا در دریافت دسته‌بندی‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Create a new design category", request=DesignCategorySerializer, responses={201: DesignCategorySerializer})
    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            serializer = DesignCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating design category", e)
            return Response({'error': 'خطا در ایجاد دسته‌بندی'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FamilyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List or create families", responses={200: FamilySerializer(many=True)})
    def get(self, request):
        try:
            families = Family.objects.all()
            serializer = FamilySerializer(families, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving families", e)
            return Response({'error': 'خطا در دریافت خانواده‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Create a new family", request=FamilySerializer, responses={201: FamilySerializer})
    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            serializer = FamilySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating family", e)
            return Response({'error': 'خطا در ایجاد خانواده'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DesignListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List or create designs", responses={200: DesignSerializer(many=True)})
    def get(self, request):
        try:
            designs = Design.objects.filter(Q(is_public=True) | Q(created_by=request.user))
            category = request.query_params.get('category')
            tag = request.query_params.get('tag')
            family = request.query_params.get('family')
            search = request.query_params.get('search')
            if category:
                designs = designs.filter(categories__id=category)
            if tag:
                designs = designs.filter(tags__id=tag)
            if family:
                designs = designs.filter(families__id=family)
            if search:
                designs = designs.filter(Q(title__icontains=search) | Q(description__icontains=search))
            serializer = DesignSerializer(designs, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving designs", e)
            return Response({'error': 'خطا در دریافت طرح‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Create a new design", request=DesignSerializer, responses={201: DesignSerializer})
    def post(self, request):
        try:
            if 'product_image' in request.FILES:
                request.FILES['product_image'] = validate_file_size(request.FILES['product_image'])
                request.FILES['product_image'] = validate_file_format(request.FILES['product_image'])
            if 'svg_file' in request.FILES:
                request.FILES['svg_file'] = validate_file_size(request.FILES['svg_file'])
                request.FILES['svg_file'] = validate_file_format(request.FILES['svg_file'], ['svg'])
            
            serializer = DesignSerializer(data=request.data)
            if serializer.is_valid():
                # تنظیم خودکار designer و created_by
                design = serializer.save(
                    created_by=request.user,
                    designer=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating design", e)
            return Response({'error': 'خطا در ایجاد طرح'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DesignDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Retrieve or update a design", responses={200: DesignSerializer})
    def get(self, request, design_id):
        try:
            design = Design.objects.get(id=design_id)
            if not design.is_public and design.created_by != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            design.increment_view_count()
            serializer = DesignSerializer(design)
            return Response(serializer.data)
        except Design.DoesNotExist:
            return Response({'error': 'طرح یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving design", e)
            return Response({'error': 'خطا در دریافت طرح'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Update a design", request=DesignSerializer, responses={200: DesignSerializer})
    def put(self, request, design_id):
        try:
            design = Design.objects.get(id=design_id)
            if design.created_by != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            if 'product_image' in request.FILES:
                request.FILES['product_image'] = validate_file_size(request.FILES['product_image'])
                request.FILES['product_image'] = validate_file_format(request.FILES['product_image'])
            if 'svg_file' in request.FILES:
                request.FILES['svg_file'] = validate_file_size(request.FILES['svg_file'])
                request.FILES['svg_file'] = validate_file_format(request.FILES['svg_file'], ['svg'])
            serializer = DesignSerializer(design, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Design.DoesNotExist:
            return Response({'error': 'طرح یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating design", e)
            return Response({'error': 'خطا در به‌روزرسانی طرح'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="Delete a design", responses={204: None})
    def delete(self, request, design_id):
        try:
            design = Design.objects.get(id=design_id)
            if design.created_by != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            design.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Design.DoesNotExist:
            return Response({'error': 'طرح یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting design", e)
            return Response({'error': 'خطا در حذف طرح'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BatchUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Batch upload designs",
        description="Upload multiple design files and assign tags, categories, families, and other attributes.",
        request=None,  # به دلیل multipart/form-data
        responses={201: DesignSerializer(many=True)}
    )
    def post(self, request):
        try:
            files = request.FILES.getlist('design_files')
            category_ids = request.data.getlist('categories')
            tag_ids = request.data.getlist('tags')
            family_ids = request.data.getlist('families')
            is_public = request.data.get('is_public', True)
            status_value = request.data.get('status', 'draft')
            design_type = request.data.get('type', '')

            if not files:
                return Response({'error': 'هیچ فایلی انتخاب نشده'}, status=status.HTTP_400_BAD_REQUEST)

            designs = []
            for file in files:
                file = validate_file_size(file)
                file = validate_file_format(file, ['svg', 'png', 'jpg', 'jpeg'])
                design_data = {
                    'title': file.name.split('.')[0],
                    'description': '',
                    'product_image': file,
                    'type': design_type,
                    'status': status_value,
                    'is_public': is_public,
                }
                serializer = DesignSerializer(data=design_data)
                if serializer.is_valid():
                    design = serializer.save(created_by=request.user)
                    if category_ids:
                        design.categories.set(category_ids)
                    if tag_ids:
                        design.tags.set(tag_ids)
                    if family_ids:
                        design.families.set(family_ids)
                    designs.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(designs, status=status.HTTP_201_CREATED)
        except Exception as e:
            log_error("Error in batch upload", e)
            return Response({'error': 'خطا در آپلود دسته‌ای'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PrintLocationViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت محل‌های چاپ روی لباس"""
    queryset = PrintLocation.objects.filter(is_active=True)
    serializer_class = PrintLocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['location_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'location_type', 'price_modifier']
    ordering = ['location_type', 'name']

    def get_queryset(self):
        """فیلتر محل‌های چاپ بر اساس دسترسی کاربر"""
        queryset = super().get_queryset()
        
        # نمایش همه محل‌ها برای staff
        if self.request.user.is_staff:
            return PrintLocation.objects.all()
        
        # نمایش فقط محل‌های فعال برای سایر کاربران
        return queryset

    @action(detail=False, methods=['get'])
    def by_garment_type(self, request):
        """دریافت محل‌های چاپ بر اساس نوع لباس"""
        garment_type = request.query_params.get('type', '')
        
        # منطق فیلتر بر اساس نوع لباس
        if garment_type == 'tshirt':
            locations = self.get_queryset().filter(
                location_type__in=['front', 'back', 'sleeve_left', 'sleeve_right']
            )
        elif garment_type == 'hoodie':
            locations = self.get_queryset().filter(
                location_type__in=['front', 'back', 'sleeve_left', 'sleeve_right', 'pocket']
            )
        else:
            locations = self.get_queryset()
        
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def cost_calculator(self, request, pk=None):
        """محاسبه هزینه چاپ برای محل مشخص"""
        location = self.get_object()
        base_price = float(request.query_params.get('base_price', 0))
        complexity = int(request.query_params.get('complexity', 1))
        
        calculated_cost = location.calculate_print_cost(base_price, complexity)
        
        return Response({
            'location': location.name,
            'base_price': base_price,
            'complexity': complexity,
            'price_modifier': location.price_modifier,
            'calculated_cost': calculated_cost
        })
