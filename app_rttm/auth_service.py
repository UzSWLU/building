import requests
import logging
import hashlib
import time
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AuthService:
    """
    External auth API bilan ishlash uchun service
    """

    def __init__(self):
        self.auth_base_url = getattr(settings, 'AUTH_BASE_URL', 'https://auth.uzswlu.uz')
        self.timeout = getattr(settings, 'AUTH_TIMEOUT', 10)
        self.cache_timeout = getattr(settings, 'AUTH_CACHE_TIMEOUT', 300)  # 5 minut
        self.max_retries = 3

    def _get_cache_key(self, prefix: str, access_token: str) -> str:
        """
        Cache key ni xavfsiz tarzda hosil qilish (tokenni hash qilish)
        """
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()[:16]
        return f"{prefix}_{token_hash}"

    def invalidate_cache(self, access_token: str):
        """
        Token uchun cache ni tozalash (logout da ishlatiladi)
        """
        keys = [
            self._get_cache_key("auth_user_role", access_token),
            self._get_cache_key("auth_user_info", access_token),
        ]
        for key in keys:
            cache.delete(key)
        logger.info("Cache tozalandi")

    def get_current_user_role(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Access token orqali user role olish (retry mexanizmi bilan)
        """
        if not access_token:
            return None

        # Cache dan tekshirish
        cache_key = self._get_cache_key("auth_user_role", access_token)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache dan user role olindi")
            return cached_result

        # Retry mexanizmi
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }

                url = f"{self.auth_base_url}/api/auth/my-role"

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Auth API dan user role olindi: {user_data.get('username', 'Unknown')}")

                    # Cache ga saqlash
                    cache.set(cache_key, user_data, self.cache_timeout)
                    return user_data
                elif response.status_code == 401:
                    # Token noto'g'ri - retry qilmaslik
                    logger.warning(f"Auth API: Unauthorized token")
                    return None
                else:
                    logger.warning(f"Auth API xatosi: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    return None

            except requests.exceptions.Timeout:
                logger.error(f"Auth API timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                return None
            except requests.exceptions.ConnectionError:
                logger.error(f"Auth API connection error (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                logger.error(f"User role olishda kutilmagan xatolik: {e}")
                return None

        return None

    def verify_token(self, access_token: str) -> bool:
        """
        Access token ni tekshirish - get_current_user_role orqali
        """
        if not access_token:
            return False

        # Dublikatni oldini olish - get_current_user_role ni ishlatamiz
        user_role_data = self.get_current_user_role(access_token)
        return user_role_data is not None

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Access token orqali user ma'lumotlarini olish
        Agar alohida endpoint mavjud bo'lsa ishlatiladi
        """
        if not access_token:
            return None

        # Cache dan tekshirish
        cache_key = self._get_cache_key("auth_user_info", access_token)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache dan user info olindi")
            return cached_result

        for attempt in range(self.max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }

                # To'g'ri URL - auth servisingizga qarab o'zgartiring
                url = f"{self.auth_base_url}/api/auth/me"  # yoki /api/auth/current-user

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Auth API dan user info olindi")

                    # Cache ga saqlash
                    cache.set(cache_key, user_data, self.cache_timeout)
                    return user_data
                elif response.status_code == 401:
                    logger.warning(f"User info API: Unauthorized")
                    return None
                elif response.status_code == 404:
                    # Endpoint mavjud emas - get_current_user_role dan ma'lumot olamiz
                    logger.info("User info endpoint mavjud emas, role endpoint ishlatiladi")
                    return self.get_current_user_role(access_token)
                else:
                    logger.warning(f"User info API xatosi: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    # Fallback - role endpoint ishlatish
                    return self.get_current_user_role(access_token)

            except requests.exceptions.Timeout:
                logger.error(f"User info API timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    continue
                # Fallback
                return self.get_current_user_role(access_token)
            except requests.exceptions.ConnectionError:
                logger.error(f"User info API connection error (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                # Fallback
                return self.get_current_user_role(access_token)
            except Exception as e:
                logger.error(f"User info olishda kutilmagan xatolik: {e}")
                # Fallback
                return self.get_current_user_role(access_token)

        # Agar barcha urinishlar muvaffaqiyatsiz bo'lsa
        return self.get_current_user_role(access_token)

    def has_permission(self, access_token: str, required_roles: list = None) -> bool:
        """
        User da kerakli role borligini tekshirish
        """
        if not access_token:
            return False

        user_role_data = self.get_current_user_role(access_token)
        if not user_role_data:
            return False

        # Agar role tekshirish kerak bo'lmasa, faqat token validligini tekshirish
        if not required_roles:
            return True

        user_role = user_role_data.get('role', '').lower()
        logger.info(f"User role: {user_role}, Required roles: {required_roles}")

        # Admin va creator role larini tekshirish
        allowed_roles = ['admin', 'creator', 'creater']  # creator va creater ikkalasini ham qo'llab-quvvatlash
        required_roles_lower = [role.lower() for role in required_roles]

        return user_role in required_roles_lower or user_role in allowed_roles


# Global instance
auth_service = AuthService()