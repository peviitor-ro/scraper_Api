from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from .models import Users, Newsletter

User = get_user_model()


class NewsletterUsersModelTest(TestCase):
    """Test cases for Newsletter Users model"""
    
    def test_users_creation(self):
        """Test creating a newsletter user instance"""
        newsletter_user = Users.objects.create(
            email='newsletter@example.com'
        )
        
        self.assertEqual(newsletter_user.email, 'newsletter@example.com')
        self.assertEqual(str(newsletter_user), 'newsletter@example.com')
    
    def test_users_email_unique(self):
        """Test that newsletter user email must be unique"""
        Users.objects.create(email='newsletter@example.com')
        
        with self.assertRaises(Exception):
            Users.objects.create(email='newsletter@example.com')


class NewsletterModelTest(TestCase):
    """Test cases for Newsletter model"""
    
    def setUp(self):
        self.newsletter_user = Users.objects.create(
            email='newsletter@example.com'
        )
    
    def test_newsletter_creation(self):
        """Test creating a newsletter instance"""
        newsletter = Newsletter.objects.create(
            email=self.newsletter_user,
            job_title='Software Developer',
            city='Bucharest',
            job_type='Full-time',
            company='Test Company'
        )
        
        self.assertEqual(newsletter.email, self.newsletter_user)
        self.assertEqual(newsletter.job_title, 'Software Developer')
        self.assertEqual(newsletter.city, 'Bucharest')
        self.assertEqual(newsletter.job_type, 'Full-time')
        self.assertEqual(newsletter.company, 'Test Company')
        self.assertEqual(str(newsletter), 'newsletter@example.com')
    
    def test_newsletter_with_blank_fields(self):
        """Test creating newsletter with blank optional fields"""
        newsletter = Newsletter.objects.create(
            email=self.newsletter_user
        )
        
        self.assertEqual(newsletter.email, self.newsletter_user)
        self.assertEqual(newsletter.job_title, '')
        self.assertEqual(newsletter.city, '')
        self.assertEqual(newsletter.job_type, '')
        self.assertEqual(newsletter.company, '')
    
    def test_newsletter_clean_data(self):
        """Test newsletter clean_data method"""
        newsletter = Newsletter.objects.create(
            email=self.newsletter_user,
            job_title='Software Developer',
            city='Bucharest',
            job_type='Full-time',
            company='Test Company'
        )
        
        newsletter.clean_data()
        
        self.assertEqual(newsletter.job_title, '')
        self.assertEqual(newsletter.city, '')
        self.assertEqual(newsletter.job_type, '')
        self.assertEqual(newsletter.company, '')
    
    def test_newsletter_foreign_key_cascade(self):
        """Test that deleting user cascades to newsletter"""
        newsletter = Newsletter.objects.create(
            email=self.newsletter_user,
            job_title='Software Developer'
        )
        
        self.newsletter_user.delete()
        
        with self.assertRaises(Newsletter.DoesNotExist):
            Newsletter.objects.get(id=newsletter.id)


class NewsletterViewsTest(APITestCase):
    """Test cases for Newsletter views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.newsletter_user = Users.objects.create(
            email='newsletter@example.com'
        )
        self.newsletter = Newsletter.objects.create(
            email=self.newsletter_user,
            job_title='Software Developer',
            city='Bucharest'
        )
    
    def test_newsletter_subscription_view(self):
        """Test newsletter subscription endpoint"""
        data = {
            'email': 'newsubscriber@example.com',
            'job_title': 'Frontend Developer',
            'city': 'Cluj',
            'job_type': 'Remote',
            'company': 'Tech Company'
        }
        
        # This would test the actual subscription endpoint
        # Implementation depends on the actual view structure
        # Typically would be something like:
        # response = self.client.post(reverse('newsletter:subscribe'), data)
        # self.assertEqual(response.status_code, 201)
    
    def test_newsletter_list_view(self):
        """Test newsletter list API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual newsletter list endpoint
        # Implementation depends on the actual view structure
    
    def test_newsletter_update_preferences_view(self):
        """Test newsletter preference update endpoint"""
        data = {
            'job_title': 'Senior Software Developer',
            'city': 'Bucharest, Cluj',
            'job_type': 'Full-time, Remote'
        }
        
        # This would test the actual preference update endpoint
        # Implementation depends on the actual view structure
    
    def test_newsletter_unsubscribe_view(self):
        """Test newsletter unsubscribe endpoint"""
        data = {
            'email': 'newsletter@example.com'
        }
        
        # This would test the actual unsubscribe endpoint
        # Implementation depends on the actual view structure
    
    @patch('newsletter.task.send_newsletter_email')
    def test_newsletter_send_task(self, mock_send_email):
        """Test newsletter sending task"""
        mock_send_email.return_value = True
        
        # This would test the actual newsletter sending task
        # Implementation depends on the actual task structure
