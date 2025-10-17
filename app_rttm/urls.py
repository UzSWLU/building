from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BuildingViewSet, BuildingImageViewSet,
    RoomViewSet, RoomImageViewSet,
    ResponsiblePersonViewSet,
    CategoryViewSet,
    DeviceTypeViewSet,
    DeviceViewSet, DeviceImageViewSet,
    DeviceLocationViewSet, DeviceLocationHistoryViewSet, DeviceConditionHistoryViewSet,
    RepairRequestViewSet, ServiceLogViewSet,
)

router = DefaultRouter()
router.register('buildings', BuildingViewSet)
router.register('building-images', BuildingImageViewSet)
router.register('rooms', RoomViewSet)
router.register('room-images', RoomImageViewSet)
router.register('responsibles', ResponsiblePersonViewSet)
router.register('categories', CategoryViewSet)
router.register('device-types', DeviceTypeViewSet)
router.register('devices', DeviceViewSet)
router.register('device-images', DeviceImageViewSet)
router.register('device-locations', DeviceLocationViewSet)
router.register('device-location-history', DeviceLocationHistoryViewSet, basename='device-location-history')
router.register('device-condition-history', DeviceConditionHistoryViewSet, basename='device-condition-history')
router.register('repair-requests', RepairRequestViewSet)
router.register('service-logs', ServiceLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


