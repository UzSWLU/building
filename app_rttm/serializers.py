from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
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

User = get_user_model()


class RoomFilterSerializer(serializers.Serializer):
    """Room filtering by building"""
    building_id = serializers.IntegerField()


class DeviceMoveSerializer(serializers.Serializer):
    """Device move action"""
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    responsible_person = serializers.PrimaryKeyRelatedField(
        queryset=ResponsiblePerson.objects.all(),
        required=False,
        allow_null=True
    )
    reason = serializers.CharField(required=False, allow_blank=True)


class DeviceChangeConditionSerializer(serializers.Serializer):
    """Device condition change action"""
    new_condition = serializers.ChoiceField(choices=Device.CONDITION_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)


class BuildingSerializer(serializers.ModelSerializer):
    """Bino ma'lumotlari"""

    class Meta:
        model = Building
        fields = (
            'id',
            'name',
            'description',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')



class BuildingImageSerializer(serializers.ModelSerializer):
    """Bino rasmlari"""

    class Meta:
        model = BuildingImage
        fields = (
            'id',
            'building',
            'image',
            "is_main",
            'title',
            'uploaded_at',
        )
        read_only_fields = ('id', 'uploaded_at')

class BuildingImageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating building images.

    This serializer is used for handling the creation of building image objects.
    It ensures that only the required attributes for creating building images are
    processed and stored properly.
    """
    building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
    image = serializers.ListField(child=serializers.ImageField(),
                                  write_only=True,
                                  help_text='bir nechta rams yubish'
                                  )


    def create(self, validated_data):
        building = validated_data.pop('building')
        title = validated_data.pop('title')
        is_main = validated_data.pop('is_main')
        images = validated_data.pop('image')
        building_image = BuildingImage.objects.create(building=building, **validated_data)
        for image in images:
            building_image.image.save(image.name, image, title, is_main)
            building_image.save(
                update_fields=['image', 'title', 'is_main']
            )
        return building_image

class RoomSerializer(serializers.ModelSerializer):
    """Xona ma'lumotlari"""
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Room
        fields = (
            'id',
            'building',
            'building_name',
            'name',
            'description',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class RoomImageSerializer(serializers.ModelSerializer):
    """Xona rasmlari"""

    class Meta:
        model = RoomImage
        fields = (
            'id',
            'room',
            'image',
            'is_main',
            'uploaded_at',
        )
        read_only_fields = ('id', 'uploaded_at')


class ResponsiblePersonSerializer(serializers.ModelSerializer):
    """Mas'ul shaxslar"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = ResponsiblePerson
        fields = (
            'id',
            'user',
            'user_username',
            'building',
            'building_name',
            'room',
            'room_name',
            'position',
            'phone',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class CategorySerializer(serializers.ModelSerializer):
    """Qurilma kategoriyalari"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'parent',
            'parent_name',
            'name',
            'code',
            'description',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class DeviceTypeSerializer(serializers.ModelSerializer):
    """Qurilma turlari"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = DeviceType
        fields = (
            'id',
            'category',
            'category_name',
            'name',
            'model',
            'manufacturer',
            'picture',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class DeviceSerializer(serializers.ModelSerializer):
    """Qurilmalar"""
    device_type_name = serializers.CharField(source='device_type.name', read_only=True)
    category_name = serializers.CharField(source='device_type.category.name', read_only=True)

    class Meta:
        model = Device
        fields = (
            'id',
            'device_type',
            'device_type_name',
            'category_name',
            'inventory_number',
            'serial_number',
            'condition',
            'purchase_date',
            'purchase_price',
            'ip_address',
            'mac_address',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')

    def validate_inventory_number(self, value):
        """Inventar raqamini tekshirish"""
        if self.instance:  # Update paytida
            if Device.objects.exclude(pk=self.instance.pk).filter(inventory_number=value).exists():
                raise serializers.ValidationError("Bu inventar raqam allaqachon mavjud")
        else:  # Create paytida
            if Device.objects.filter(inventory_number=value).exists():
                raise serializers.ValidationError("Bu inventar raqam allaqachon mavjud")
        return value


class DeviceImageSerializer(serializers.ModelSerializer):
    """Qurilma rasmlari"""

    class Meta:
        model = DeviceImage
        fields = (
            'id',
            'device',
            'image',
            'is_main',
            'uploaded_at',
        )
        read_only_fields = ('id', 'uploaded_at')


class DeviceLocationSerializer(serializers.ModelSerializer):
    """Qurilma joylashuvi"""
    device_info = serializers.CharField(source='device.inventory_number', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    building_name = serializers.CharField(source='room.building.name', read_only=True)
    responsible_name = serializers.CharField(source='responsible_person.user.username', read_only=True)

    class Meta:
        model = DeviceLocation
        fields = (
            'id',
            'device',
            'device_info',
            'room',
            'room_name',
            'building_name',
            'responsible_person',
            'responsible_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class DeviceLocationHistorySerializer(serializers.ModelSerializer):
    """Qurilma ko'chirish tarixi"""
    device_info = serializers.CharField(source='device.inventory_number', read_only=True)
    old_building_name = serializers.CharField(source='old_building.name', read_only=True)
    old_room_name = serializers.CharField(source='old_room.name', read_only=True)
    new_building_name = serializers.CharField(source='new_building.name', read_only=True)
    new_room_name = serializers.CharField(source='new_room.name', read_only=True)
    moved_by_username = serializers.CharField(source='moved_by.username', read_only=True)

    class Meta:
        model = DeviceLocationHistory
        fields = (
            'id',
            'device',
            'device_info',
            'old_building',
            'old_building_name',
            'old_room',
            'old_room_name',
            'new_building',
            'new_building_name',
            'new_room',
            'new_room_name',
            'moved_by',
            'moved_by_username',
            'moved_at',
            'reason',
        )
        read_only_fields = (
            'id', 'device', 'old_building', 'old_room',
            'new_building', 'new_room', 'moved_by', 'moved_at'
        )


class DeviceConditionHistorySerializer(serializers.ModelSerializer):
    """Qurilma holati tarixi"""
    device_info = serializers.CharField(source='device.inventory_number', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = DeviceConditionHistory
        fields = (
            'id',
            'device',
            'device_info',
            'old_condition',
            'new_condition',
            'changed_by',
            'changed_by_username',
            'changed_at',
            'reason',
        )
        read_only_fields = (
            'id', 'device', 'old_condition', 'new_condition',
            'changed_by', 'changed_at'
        )


class RepairRequestSerializer(serializers.ModelSerializer):
    """Ta'mirlash so'rovlari"""
    device_info = serializers.CharField(source='device.inventory_number', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = RepairRequest
        fields = (
            'id',
            'device',
            'device_info',
            'requested_by',
            'requested_by_username',
            'assigned_to',
            'assigned_to_username',
            'priority',
            'request_status',
            'problem_description',
            'work_description',
            'completed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')


class ServiceLogSerializer(serializers.ModelSerializer):
    """Xizmat ko'rsatish jurnali"""
    device_info = serializers.CharField(source='device.inventory_number', read_only=True)
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = ServiceLog
        fields = (
            'id',
            'device',
            'device_info',
            'service_type',
            'service_date',
            'performed_by',
            'performed_by_username',
            'repair_request',
            'description',
            'cost',
            'next_service_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'updated_by', 'created_at', 'updated_at')