from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.management import call_command

User = get_user_model()


class BasicTestCase(TestCase):
    """Basic tests for the Building API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class APITestCase(APITestCase):
    """API tests for the Building API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
    
    def test_api_schema_endpoint(self):
        """Test API schema endpoint"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_swagger_ui_endpoint(self):
        """Test Swagger UI endpoint"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'swagger')


class ManagementCommandTestCase(TestCase):
    """Test management commands"""
    
    def test_migrate_command(self):
        """Test migrate command"""
        try:
            call_command('migrate', verbosity=0)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Migration failed: {e}")
    
    def test_check_command(self):
        """Test check command"""
        try:
            call_command('check', verbosity=0)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Check command failed: {e}")
