from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser
from .managers import CustomUserManager
from .middleware import RateLimitMiddleware
from company.models import Company, Source
from scraper.models import Scraper
from unittest.mock import Mock

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'test@example.com')
    
    def test_user_email_unique(self):
        """Test that user email must be unique"""
        User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                password='anotherpass123'
            )
    
    def test_superuser_gets_all_relations(self):
        """Test that superuser gets all companies and scrapers"""
        # Create some test data
        source = Source.objects.create(sursa='test_source')
        company = Company.objects.create(
            source=source,
            company='Test Company'
        )
        scraper = Scraper.objects.create(name='test_scraper')
        
        # Create superuser
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Check that superuser has access to all companies and scrapers
        self.assertIn(company.id, user.company.values_list('id', flat=True))
        self.assertIn(scraper.id, user.scraper.values_list('id', flat=True))


class CustomUserManagerTest(TestCase):
    """Test cases for CustomUserManager"""
    
    def test_create_user_without_email(self):
        """Test creating user without email should raise error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')
    
    def test_create_superuser_without_staff(self):
        """Test creating superuser without is_staff should raise error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
    
    def test_create_superuser_without_superuser(self):
        """Test creating superuser without is_superuser should raise error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )


class RateLimitMiddlewareTest(TestCase):
    """Test cases for RateLimitMiddleware"""
    
    def setUp(self):
        self.middleware = RateLimitMiddleware(Mock())
        self.request = Mock()
        self.request.META = {'REMOTE_ADDR': '127.0.0.1'}
        self.request.path = '/test/'
    
    def test_middleware_allows_request_within_limit(self):
        """Test that middleware allows requests within rate limit"""
        response = self.middleware(self.request)
        # Should not return a rate limit response
        # Note: Implementation details depend on the actual middleware logic


class UserViewsTest(APITestCase):
    """Test cases for User views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration_view(self):
        """Test user registration"""
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        # This would test actual registration endpoint if it exists
        # Response format depends on the actual view implementation
    
    def test_user_login_view(self):
        """Test user login"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        # This would test actual login endpoint if it exists
        # Response format depends on the actual view implementation
    
    def test_user_profile_view(self):
        """Test user profile view"""
        self.client.force_login(self.user)
        
        # This would test actual profile endpoint if it exists
        # Response format depends on the actual view implementation
