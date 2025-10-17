from django.contrib import admin
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


class BuildingImageInline(admin.TabularInline):
    model = BuildingImage
    extra = 0


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'status', 'created_at')
    search_fields = ('name',)
    inlines = [BuildingImageInline]


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('building', 'name', 'status', 'created_at')
    search_fields = ('name', 'building__name')
    list_filter = ('building',)
    inlines = [RoomImageInline]


@admin.register(ResponsiblePerson)
class ResponsiblePersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'building', 'room', 'position')
    search_fields = ('user__username', 'position')
    list_filter = ('building', 'room')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent')
    search_fields = ('name', 'code')


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'manufacturer')
    search_fields = ('name', 'model', 'manufacturer')
    list_filter = ('category',)


class DeviceImageInline(admin.TabularInline):
    model = DeviceImage
    extra = 0


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'device_type', 'condition', 'purchase_date')
    search_fields = ('inventory_number', 'serial_number')
    list_filter = ('condition', 'device_type__category')
    inlines = [DeviceImageInline]


@admin.register(DeviceLocation)
class DeviceLocationAdmin(admin.ModelAdmin):
    list_display = ('device', 'room', 'responsible_person')
    list_filter = ('room', 'responsible_person')


@admin.register(DeviceLocationHistory)
class DeviceLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('device', 'old_room', 'new_room', 'moved_by', 'moved_at')
    list_filter = ('new_room', 'old_room')


@admin.register(DeviceConditionHistory)
class DeviceConditionHistoryAdmin(admin.ModelAdmin):
    list_display = ('device', 'old_condition', 'new_condition', 'changed_by', 'changed_at')
    list_filter = ('new_condition',)


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'priority', 'request_status', 'created_at')
    list_filter = ('priority', 'request_status')
    search_fields = ('device__inventory_number',)


@admin.register(ServiceLog)
class ServiceLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'service_type', 'service_date')
    list_filter = ('service_type',)
