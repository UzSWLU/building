from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema_view, extend_schema, OpenApiExample,
    OpenApiParameter, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import AuthPermission, AdminOnlyPermission, ReadOnlyPermission, SmartPermission

from .models import (
    Building, BuildingImage,
    Room, RoomImage,
    ResponsiblePerson,
    Category,
    DeviceType,
    Device, DeviceImage,
    DeviceLocation, DeviceLocationHistory, DeviceConditionHistory,
    RepairRequest, ServiceLog,
)
from .serializers import (
    BuildingSerializer, BuildingImageSerializer,BuildingImageCreateSerializer,
    RoomSerializer, RoomImageSerializer,
    ResponsiblePersonSerializer,
    CategorySerializer,
    DeviceTypeSerializer,
    DeviceSerializer, DeviceImageSerializer,
    DeviceLocationSerializer, DeviceLocationHistorySerializer, DeviceConditionHistorySerializer,
    RepairRequestSerializer, ServiceLogSerializer,
    RoomFilterSerializer, DeviceMoveSerializer, DeviceChangeConditionSerializer,
)


# Auth permission classes
class DefaultPermissions(SmartPermission):
    pass

class AdminOnlyPermissions(AdminOnlyPermission):
    pass

class ReadOnlyPermissions(ReadOnlyPermission):
    pass


@extend_schema_view(
    list=extend_schema(
        summary="Barcha binolar ro'yxati",
        description="Tizimda mavjud barcha binolarni olish",
        tags=['Buildings']
    ),
    retrieve=extend_schema(
        summary="Bitta binoni olish",
        description="ID bo'yicha bitta binoni batafsil ma'lumot bilan olish",
        tags=['Buildings']
    ),
    create=extend_schema(
        summary="Yangi bino qo'shish",
        description="Yangi bino yaratish. JSON yoki form-data formatida yuborish mumkin.",
        tags=['Buildings'],
        request=BuildingSerializer,
        examples=[
            OpenApiExample(
                'JSON format',
                value={
                    'name': 'Asosiy korpus',
                    'description': 'Asosiy o\'quv binosi',
                    'status': 'active'
                },
                request_only=True,
            ),
        ]
    ),
    update=extend_schema(
        summary="Binoni yangilash",
        description="Mavjud binoni to'liq yangilash.",
        tags=['Buildings'],
        request=BuildingSerializer,
    ),
    partial_update=extend_schema(
        summary="Binoni qisman yangilash",
        description="Binoning faqat ba'zi maydonlarini yangilash.",
        tags=['Buildings'],
        request=BuildingSerializer,
    ),
    destroy=extend_schema(
        summary="Binoni o'chirish",
        description="Binoni tizimdan butunlay o'chirish.",
        tags=['Buildings']
    ),
)
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [DefaultPermissions]

    # MUHIM: Bu parsers qo'shildi - form-data va JSON formatlarini qabul qilish uchun
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


@extend_schema_view(
    create=extend_schema(
        summary="Bino rasmini yuklash",
        description="Bino uchun yangi rasm yuklash (multipart/form-data formatida)",
        tags=['Buildings'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'building': {'type': 'integer', 'description': 'Bino ID'},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'Rasm fayli'},
                    'is_main': {'type': 'boolean', 'description': 'Asosiy rasm'}
                },
                'required': ['building', 'image']
            }
        },
        responses={201: BuildingImageSerializer}
    ),
    list=extend_schema(
        summary="Bino rasmlar ro'yxati",
        description="Barcha bino rasmlarini filtrlash bilan olish",
        tags=['Buildings'],
    ),
    retrieve=extend_schema(
        summary="Bino rasmini olish",
        description="Bitta bino rasmini olish",
        tags=['Buildings'],
    ),
    update=extend_schema(
        summary="Bino rasmini yangilash",
        description="Bino rasm ma'lumotlarini yangilash",
        tags=['Buildings'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'building': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    partial_update=extend_schema(
        summary="Bino rasmini qisman yangilash",
        description="Bino rasmining ba'zi maydonlarini yangilash",
        tags=['Buildings'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    destroy=extend_schema(
        summary="Bino rasmini o'chirish",
        description="Bino rasmini o'chirish",
        tags=['Buildings'],
    ),
)
class BuildingImageViewSet(viewsets.ModelViewSet):
    queryset = BuildingImage.objects.all()
    serializer_class = BuildingImageSerializer
    permission_classes = [DefaultPermissions]

    # MUHIM: Rasmlar uchun multipart parser kerak
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['building']
    ordering_fields = ['uploaded_at']

    @extend_schema(
        summary="Bir nechta rasm yuklash (bino)",
        description="Bitta so'rovda bir nechta rasmni bino uchun yuklash",
        tags=['Buildings'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'building': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['building', 'images']
            }
        },
        responses={201: BuildingImageSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_upload(self, request):
        building_id = request.data.get('building')
        files = request.FILES.getlist('images')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if not building_id:
            return Response({'detail': 'building is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not files:
            return Response({'detail': 'images are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            return Response({'detail': 'building not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for f in files:
            obj = BuildingImage.objects.create(building=building, image=f, is_main=is_main, title=title or None)
            created.append(obj)
        return Response(BuildingImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Bino uchun rasm(lar) yuklash",
        description="Default POST ham bir nechta faylni qabul qiladi",
        tags=['Buildings'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'building': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['building']
            }
        },
        responses={201: BuildingImageSerializer(many=True)}
    )
    def create(self, request, *args, **kwargs):
        building_id = request.data.get('building')
        if not building_id:
            return Response({'detail': 'building is required'}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('images') or request.FILES.getlist('image')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if files:
            try:
                building = Building.objects.get(pk=building_id)
            except Building.DoesNotExist:
                return Response({'detail': 'building not found'}, status=status.HTTP_404_NOT_FOUND)

            created = []
            for f in files:
                obj = BuildingImage.objects.create(building=building, image=f, is_main=is_main, title=title or None)
                created.append(obj)
            return Response(BuildingImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(tags=['Rooms']),
    retrieve=extend_schema(tags=['Rooms']),
    create=extend_schema(
        tags=['Rooms'],
        request=RoomSerializer,
    ),
    update=extend_schema(
        tags=['Rooms'],
        request=RoomSerializer,
    ),
    partial_update=extend_schema(
        tags=['Rooms'],
        request=RoomSerializer,
    ),
    destroy=extend_schema(tags=['Rooms']),
)
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('building').all()
    serializer_class = RoomSerializer
    permission_classes = [DefaultPermissions]

    # JSON va form-data formatlarini qabul qilish
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building']
    search_fields = ['name', 'description', 'building__name']
    ordering_fields = ['name', 'created_at']

    @extend_schema(
        summary="Binoga qarab xonalarni olish",
        description="Ma'lum bino uchun barcha xonalarni olish",
        tags=['Rooms'],
        parameters=[
            OpenApiParameter(
                name='building_id',
                description='Xonalarni filtrlash uchun bino ID',
                required=True,
                type=int,
                location='query'
            )
        ],
        responses={200: RoomSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], serializer_class=RoomSerializer)
    def by_building(self, request):
        """Get rooms filtered by building ID"""
        building_id = request.query_params.get('building_id')
        if not building_id:
            return Response({'error': 'building_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rooms = Room.objects.filter(building_id=building_id).select_related('building')
            serializer = self.get_serializer(rooms, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    create=extend_schema(
        summary="Xona rasmini yuklash",
        description="Xona uchun yangi rasm yuklash",
        tags=['Rooms'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'room': {'type': 'integer', 'description': 'Xona ID'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                },
                'required': ['room', 'image']
            }
        },
    ),
    list=extend_schema(tags=['Rooms']),
    retrieve=extend_schema(tags=['Rooms']),
    update=extend_schema(
        tags=['Rooms'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'room': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    partial_update=extend_schema(
        tags=['Rooms'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    destroy=extend_schema(tags=['Rooms']),
)
class RoomImageViewSet(viewsets.ModelViewSet):
    queryset = RoomImage.objects.select_related('room').all()
    serializer_class = RoomImageSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room']
    ordering_fields = ['uploaded_at']

    @extend_schema(
        summary="Bir nechta rasm yuklash (xona)",
        description="Xona uchun bir nechta rasm yuklash",
        tags=['Rooms'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'room': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['room', 'images']
            }
        },
        responses={201: RoomImageSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_upload(self, request):
        room_id = request.data.get('room')
        files = request.FILES.getlist('images')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if not room_id:
            return Response({'detail': 'room talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)
        if not files:
            return Response({'detail': 'images talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.select_related('building').get(pk=room_id)
        except Room.DoesNotExist:
            return Response({'detail': 'room not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for f in files:
            obj = RoomImage.objects.create(room=room, image=f, is_main=is_main, title=title or None)
            created.append(obj)
        return Response(RoomImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Xona uchun rasm(lar) yuklash",
        description="Default POST ham bir nechta faylni qabul qiladi",
        tags=['Rooms'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'room': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['room']
            }
        },
        responses={201: RoomImageSerializer(many=True)}
    )
    def create(self, request, *args, **kwargs):
        room_id = request.data.get('room')
        if not room_id:
            return Response({'detail': 'room is required'}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('images') or request.FILES.getlist('image')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if files:
            try:
                room = Room.objects.get(pk=room_id)
            except Room.DoesNotExist:
                return Response({'detail': 'room not found'}, status=status.HTTP_404_NOT_FOUND)

            created = []
            for f in files:
                obj = RoomImage.objects.create(room=room, image=f, is_main=is_main, title=title or None)
                created.append(obj)
            return Response(RoomImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(tags=['Responsible Persons']),
    retrieve=extend_schema(tags=['Responsible Persons']),
    create=extend_schema(
        tags=['Responsible Persons'],
        request=ResponsiblePersonSerializer,
    ),
    update=extend_schema(
        tags=['Responsible Persons'],
        request=ResponsiblePersonSerializer,
    ),
    partial_update=extend_schema(
        tags=['Responsible Persons'],
        request=ResponsiblePersonSerializer,
    ),
    destroy=extend_schema(tags=['Responsible Persons']),
)
class ResponsiblePersonViewSet(viewsets.ModelViewSet):
    queryset = ResponsiblePerson.objects.select_related('user', 'building', 'room').all()
    serializer_class = ResponsiblePersonSerializer
    permission_classes = [AdminOnlyPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'room', 'user']
    search_fields = ['position', 'phone', 'user__username']
    ordering_fields = ['created_at']


@extend_schema_view(
    list=extend_schema(tags=['Categories']),
    retrieve=extend_schema(tags=['Categories']),
    create=extend_schema(tags=['Categories'], request=CategorySerializer),
    update=extend_schema(tags=['Categories'], request=CategorySerializer),
    partial_update=extend_schema(tags=['Categories'], request=CategorySerializer),
    destroy=extend_schema(tags=['Categories']),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all()
    serializer_class = CategorySerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']


@extend_schema_view(
    list=extend_schema(tags=['Device Types']),
    retrieve=extend_schema(tags=['Device Types']),
    create=extend_schema(
        tags=['Device Types'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'category': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'model': {'type': 'string'},
                    'manufacturer': {'type': 'string'},
                    'picture': {'type': 'string', 'format': 'binary'}
                },
                'required': ['category', 'name']
            }
        },
    ),
    update=extend_schema(
        tags=['Device Types'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'category': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'model': {'type': 'string'},
                    'manufacturer': {'type': 'string'},
                    'picture': {'type': 'string', 'format': 'binary'}
                }
            }
        },
    ),
    partial_update=extend_schema(
        tags=['Device Types'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'picture': {'type': 'string', 'format': 'binary'}
                }
            }
        },
    ),
    destroy=extend_schema(tags=['Device Types']),
)
class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.select_related('category').all()
    serializer_class = DeviceTypeSerializer
    permission_classes = [DefaultPermissions]

    # DeviceType da picture maydoni bor, shuning uchun multipart kerak
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'model', 'manufacturer']
    ordering_fields = ['name', 'created_at']


@extend_schema_view(
    list=extend_schema(tags=['Devices']),
    retrieve=extend_schema(tags=['Devices']),
    create=extend_schema(tags=['Devices'], request=DeviceSerializer),
    update=extend_schema(tags=['Devices'], request=DeviceSerializer),
    partial_update=extend_schema(tags=['Devices'], request=DeviceSerializer),
    destroy=extend_schema(tags=['Devices']),
)
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('device_type', 'device_type__category').all()
    serializer_class = DeviceSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device_type', 'device_type__category', 'condition']
    search_fields = ['inventory_number', 'serial_number', 'notes']
    ordering_fields = ['inventory_number', 'created_at']

    @extend_schema(
        summary="Qurilmani ko'chirish",
        description="Qurilmani yangi xonaga ko'chirish va mas'ul shaxsni tayinlash",
        tags=['Devices'],
        request=DeviceMoveSerializer,
        responses={200: DeviceLocationSerializer}
    )
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        device = self.get_object()
        serializer = DeviceMoveSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        room = serializer.validated_data['room']
        responsible = serializer.validated_data.get('responsible_person')
        reason = serializer.validated_data.get('reason', '')

        with transaction.atomic():
            old_building = device.location.room.building if hasattr(device, 'location') else None
            old_room = device.location.room if hasattr(device, 'location') else None

            location, _ = DeviceLocation.objects.update_or_create(
                device=device,
                defaults={
                    'room': room,
                    'responsible_person': responsible,
                }
            )

            DeviceLocationHistory.objects.create(
                device=device,
                old_building=old_building,
                old_room=old_room,
                new_building=room.building,
                new_room=room,
                moved_by=request.user if request.user.is_authenticated else None,
                reason=reason,
            )

        return Response(DeviceLocationSerializer(location).data)

    @extend_schema(
        summary="Qurilma holatini o'zgartirish",
        description="Qurilma holatini o'zgartirish va tarixda saqlash",
        tags=['Devices'],
        request=DeviceChangeConditionSerializer,
        responses={200: DeviceConditionHistorySerializer}
    )
    @action(detail=True, methods=['post'])
    def change_condition(self, request, pk=None):
        device = self.get_object()
        serializer = DeviceChangeConditionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_condition = serializer.validated_data['new_condition']
        reason = serializer.validated_data.get('reason', '')

        with transaction.atomic():
            old = device.condition
            if old == new_condition:
                return Response({'detail': 'condition unchanged'}, status=status.HTTP_400_BAD_REQUEST)
            device.condition = new_condition
            device.save(update_fields=['condition', 'updated_at', 'updated_by'])
            history = DeviceConditionHistory.objects.create(
                device=device,
                old_condition=old,
                new_condition=new_condition,
                changed_by=request.user if request.user.is_authenticated else None,
                reason=reason,
            )

        return Response(DeviceConditionHistorySerializer(history).data)


@extend_schema_view(
    create=extend_schema(
        summary="Qurilma rasmini yuklash",
        description="Qurilma uchun yangi rasm yuklash",
        tags=['Devices'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'device': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                },
                'required': ['device', 'image']
            }
        },
    ),
    list=extend_schema(tags=['Devices']),
    retrieve=extend_schema(tags=['Devices']),
    update=extend_schema(
        tags=['Devices'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'device': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    partial_update=extend_schema(
        tags=['Devices'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'},
                    'is_main': {'type': 'boolean'}
                }
            }
        },
    ),
    destroy=extend_schema(tags=['Devices']),
)
class DeviceImageViewSet(viewsets.ModelViewSet):
    queryset = DeviceImage.objects.select_related('device').all()
    serializer_class = DeviceImageSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device']
    ordering_fields = ['uploaded_at']

    @extend_schema(
        summary="Bir nechta rasm yuklash (qurilma)",
        description="Bitta so'rovda bir nechta rasmni qurilma uchun yuklash",
        tags=['Devices'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'device': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['device', 'images']
            }
        },
        responses={201: DeviceImageSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_upload(self, request):
        device_id = request.data.get('device')
        files = request.FILES.getlist('images')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if not device_id:
            return Response({'detail': 'device is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not files:
            return Response({'detail': 'images are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            return Response({'detail': 'device not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for f in files:
            obj = DeviceImage.objects.create(device=device, image=f, is_main=is_main, title=title or None)
            created.append(obj)
        return Response(DeviceImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Qurilma uchun rasm(lar) yuklash",
        description="Default POST ham bir nechta faylni qabul qiladi",
        tags=['Devices'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'device': {'type': 'integer'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'}
                    },
                    'is_main': {'type': 'boolean'},
                    'title': {'type': 'string'}
                },
                'required': ['device']
            }
        },
        responses={201: DeviceImageSerializer(many=True)}
    )
    def create(self, request, *args, **kwargs):
        device_id = request.data.get('device')
        if not device_id:
            return Response({'detail': 'device is required'}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('images') or request.FILES.getlist('image')
        is_main = str(request.data.get('is_main', 'false')).lower() == 'true'
        title = request.data.get('title', '')

        if files:
            try:
                device = Device.objects.get(pk=device_id)
            except Device.DoesNotExist:
                return Response({'detail': 'device not found'}, status=status.HTTP_404_NOT_FOUND)

            created = []
            for f in files:
                obj = DeviceImage.objects.create(device=device, image=f, is_main=is_main, title=title or None)
                created.append(obj)
            return Response(DeviceImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(tags=['Device Locations']),
    retrieve=extend_schema(tags=['Device Locations']),
    create=extend_schema(tags=['Device Locations']),
    update=extend_schema(tags=['Device Locations']),
    partial_update=extend_schema(tags=['Device Locations']),
    destroy=extend_schema(tags=['Device Locations']),
)
class DeviceLocationViewSet(viewsets.ModelViewSet):
    queryset = DeviceLocation.objects.select_related('device', 'room').all()
    serializer_class = DeviceLocationSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'responsible_person']


@extend_schema_view(
    list=extend_schema(tags=['Device History']),
    retrieve=extend_schema(tags=['Device History']),
)
class DeviceLocationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeviceLocationHistory.objects.select_related('device', 'new_room', 'old_room').all()
    serializer_class = DeviceLocationHistorySerializer
    permission_classes = [ReadOnlyPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device', 'new_room', 'old_room']


@extend_schema_view(
    list=extend_schema(tags=['Device History']),
    retrieve=extend_schema(tags=['Device History']),
)
class DeviceConditionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeviceConditionHistory.objects.select_related('device').all()
    serializer_class = DeviceConditionHistorySerializer
    permission_classes = [ReadOnlyPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device', 'new_condition']


@extend_schema_view(
    list=extend_schema(tags=['Repairs']),
    retrieve=extend_schema(tags=['Repairs']),
    create=extend_schema(tags=['Repairs'], request=RepairRequestSerializer),
    update=extend_schema(tags=['Repairs'], request=RepairRequestSerializer),
    partial_update=extend_schema(tags=['Repairs'], request=RepairRequestSerializer),
    destroy=extend_schema(tags=['Repairs']),
)
class RepairRequestViewSet(viewsets.ModelViewSet):
    queryset = RepairRequest.objects.select_related('device', 'requested_by', 'assigned_to').all()
    serializer_class = RepairRequestSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['device', 'priority', 'request_status', 'assigned_to']
    search_fields = ['problem_description', 'work_description']
    ordering_fields = ['created_at', 'priority']


@extend_schema_view(
    list=extend_schema(tags=['Service Logs']),
    retrieve=extend_schema(tags=['Service Logs']),
    create=extend_schema(tags=['Service Logs'], request=ServiceLogSerializer),
    update=extend_schema(tags=['Service Logs'], request=ServiceLogSerializer),
    partial_update=extend_schema(tags=['Service Logs'], request=ServiceLogSerializer),
    destroy=extend_schema(tags=['Service Logs']),
)
class ServiceLogViewSet(viewsets.ModelViewSet):
    queryset = ServiceLog.objects.select_related('device', 'performed_by', 'repair_request').all()
    serializer_class = ServiceLogSerializer
    permission_classes = [DefaultPermissions]

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'service_type', 'service_date']
    ordering_fields = ['service_date', 'created_at']


# Health check endpoint
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'RTTM Django API',
        'version': '1.0.0'
    })