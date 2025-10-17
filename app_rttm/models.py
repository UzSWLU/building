import os
import re
import logging
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .middleware import get_current_user

logger = logging.getLogger(__name__)
User = get_user_model()
class RTTMMediaStorage(FileSystemStorage):
    """rttm media ichidagi fayllarni boshqaradi"""
    def __init__(self, subfolder: str = '', *args, **kwargs):
        location = os.path.join(settings.MEDIA_ROOT, 'rttmmedia', subfolder)
        os.makedirs(location, exist_ok=True)
        kwargs['location'] = location
        kwargs['base_url'] = f'{settings.MEDIA_URL}rttmmedia/{subfolder}/'
        super().__init__(*args, **kwargs)


def mac_address_validator(value):
    """MAC manzilini tekshiruvchi validator."""
    if value and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', value):
        raise ValidationError(_('Noto\'g\'ri MAC manzil formati.'))


class Main(models.Model):
    """
    Bazaviy model - created_by va updated_by AVTOMATIK.
    """
    STATUS_CHOICES = (
        ("active", _("Faol")),
        ("inactive", _("Nofaol")),
        ("archived", _("Arxivlangan")),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name=_("Holat")
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="%(class)s_createdt",
        verbose_name=_("Kim yaratdi")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan sana"))

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="%(class)s_updated",
        verbose_name=_("Kim yangiladi")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Yangilangan sana"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        AVTOMATIK USER SAQLASH - DEBUG bilan.
        """
        user = get_current_user()

        logger.info(f"save() chaqirildi. User: {user}")
        logger.info(f"User authenticated: {getattr(user, 'is_authenticated', False) if user else 'No user'}")
        logger.info(f"Model: {self.__class__.__name__}, PK: {self.pk}")

        if user and getattr(user, 'is_authenticated', False):
            if not self.pk:
                self.created_by = user
                logger.info(f"✅ created_by o'rnatildi: {user}")

            self.updated_by = user
            logger.info(f"✅ updated_by o'rnatildi: {user}")
        else:
            logger.warning(f"⚠️ User topilmadi yoki authenticated emas!")

        super().save(*args, **kwargs)


# ==================== BINOLAR ====================
building_storage = RTTMMediaStorage('building')


class Building(Main):
    name = models.CharField(max_length=255, verbose_name=_("Bino nomi"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Qisqa ma'lumot"))

    class Meta:
        verbose_name = _("Bino")
        verbose_name_plural = _("Binolar")
        ordering = ['name']

    def __str__(self):
        return self.name


class BuildingImage(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=building_storage, upload_to='buildings/%Y/%m/')
    title = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.building.name} - Rasm"


# ==================== XONALAR ====================
room_storage = RTTMMediaStorage('room')


class Room(Main):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('building', 'name')
        ordering = ['building']

    def __str__(self):
        return f"{self.building.name}"


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=room_storage, upload_to='rooms/%Y/%m/')
    title = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room} - Rasm"


# ==================== MAS'UL SHAXSLAR ====================

class ResponsiblePerson(Main):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="responsible_roles")
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="responsibles")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="responsibles")
    position = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.building.name}"


# ==================== KATEGORIYA ====================

class Category(Main):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


device_type_storage = RTTMMediaStorage('device_type')


class DeviceType(Main):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="device_types")
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(storage=device_type_storage, upload_to="device_types/%Y/%m/", blank=True, null=True)

    def __str__(self):
        return self.name


# ==================== JIHOZLAR ====================
hijoz_storage = RTTMMediaStorage('hijoz')


class Device(Main):
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, related_name="devices")
    inventory_number = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)

    CONDITION_CHOICES = (
        ('working', _("Ishlayapti")),
        ('broken', _("Buzilgan")),
        ('repair', _("Ta'mirda")),
        ('stored', _("Saqlanmoqda")),
        ('written_off', _("Hisobdan chiqarilgan")),
    )
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='working')

    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    warranty_until = models.DateField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=100, blank=True, null=True, validators=[mac_address_validator])

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device_type.name} - {self.inventory_number}"


class DeviceImage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=hijoz_storage, upload_to='devices/%Y/%m/')
    title = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.inventory_number} - Rasm"


class DeviceLocation(Main):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="location")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="current_devices")
    responsible_person = models.ForeignKey('ResponsiblePerson', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="assigned_devices")
    position_description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.device.inventory_number}"


class DeviceLocationHistory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="location_history")
    old_building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    old_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    new_building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name="+")
    new_room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="+")
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True, null=True)
    moved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-moved_at']

    def __str__(self):
        old = f"{self.old_building.name}" if self.old_building else "Yangi"
        new = f"{self.new_building.name}"
        return f"{self.device.inventory_number}: {old} → {new}"


class DeviceConditionHistory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="condition_history")
    old_condition = models.CharField(max_length=20, blank=True, null=True)
    new_condition = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        old = self.old_condition or "Yangi"
        return f"{self.device.inventory_number}: {old} → {self.new_condition}"


# ==================== TA'MIRLASH ====================

class RepairRequest(Main):
    PRIORITY_CHOICES = (
        ('low', _("Past")),
        ('medium', _("O'rta")),
        ('high', _("Yuqori")),
        ('critical', _("Juda muhim")),
    )
    REQUEST_STATUS_CHOICES = (
        ('new', _("Yangi")),
        ('assigned', _("Tayinlangan")),
        ('in_progress', _("Jarayonda")),
        ('completed', _("Bajarilgan")),
        ('cancelled', _("Bekor qilingan")),
    )

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="repair_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                     related_name="my_repair_requests")
    problem_description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    request_status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_repairs")
    assigned_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    telegram_chat_id = models.BigIntegerField(blank=True, null=True)
    telegram_message_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.device.inventory_number}"


class ServiceLog(Main):
    SERVICE_TYPE_CHOICES = (
        ('preventive', _("Profilaktika")),
        ('repair', _("Ta'mir")),
        ('inspection', _("Tekshiruv")),
        ('calibration', _("Kalibrovka")),
        ('cleaning', _("Tozalash")),
    )

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="service_logs")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    service_date = models.DateField()
    description = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="performed_services")
    cost = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    next_service_date = models.DateField(blank=True, null=True)
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="service_logs")

    class Meta:
        ordering = ['-service_date']

    def __str__(self):
        return f"{self.device.inventory_number} - {self.service_date}"
