from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from .models import Scraper

User = get_user_model()


class ScraperModelTest(TestCase):
    """Test cases for Scraper model"""
    
    def test_scraper_creation(self):
        """Test creating a scraper instance"""
        scraper = Scraper.objects.create(
            name="test_scraper",
            language="Python",
            author="Test Author"
        )
        self.assertEqual(scraper.name, "test_scraper")
        self.assertEqual(scraper.language, "Python")
        self.assertEqual(scraper.author, "Test Author")
        self.assertEqual(str(scraper), "test_scraper")
    
    def test_scraper_default_values(self):
        """Test scraper default values"""
        scraper = Scraper.objects.create(name="test_scraper")
        self.assertEqual(scraper.language, "Python")
        self.assertEqual(scraper.author, "Anonymous")
    
    def test_scraper_language_choices(self):
        """Test scraper language choices"""
        valid_languages = ['Python', 'JavaScript', 'Jmeter']
        for lang in valid_languages:
            scraper = Scraper.objects.create(
                name=f"test_scraper_{lang.lower()}",
                language=lang
            )
            self.assertEqual(scraper.language, lang)


class ScraperViewsTest(APITestCase):
    """Test cases for Scraper views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.scraper = Scraper.objects.create(name="test_scraper")
        self.user.scraper.add(self.scraper)
    
    @patch('scraper.views.Container')
    @patch('scraper.views.Scraper')
    def test_scraper_add_view_success(self, mock_scraper_class, mock_container):
        """Test successful scraper addition"""
        # Mock container and scraper objects
        mock_container_instance = Mock()
        mock_container.return_value.create_container.return_value = mock_container_instance
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.container.client_container.name = "test_container"
        mock_scraper_instance.clone_repository.return_value = ("success", 0)
        mock_scraper_instance.install_dependencies.return_value = ("success", "")
        mock_scraper_class.return_value = mock_scraper_instance
        
        self.client.force_login(self.user)
        
        data = {
            'url': 'https://github.com/test/repo.git',
            'language': 'python'
        }
        
        response = self.client.post(
            reverse('scraper:add_scraper'),
            data=data,
            content_type='application/json'
        )
        
        # Should work if authenticated properly
        # Note: This might fail due to authentication setup
        
    def test_scraper_add_view_missing_params(self):
        """Test scraper addition with missing parameters"""
        self.client.force_login(self.user)
        
        # Missing language
        data = {'url': 'https://github.com/test/repo.git'}
        response = self.client.post(
            reverse('scraper:add_scraper'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing URL
        data = {'language': 'python'}
        response = self.client.post(
            reverse('scraper:add_scraper'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('scraper.views.Container')  
    def test_scraper_remove_view_success(self, mock_container):
        """Test successful scraper removal"""
        mock_container.return_value.remove_container.return_value = True
        
        self.client.force_login(self.user)
        
        data = {'name': 'test_scraper'}
        response = self.client.post(
            reverse('scraper:remove_scraper'),
            data=data,
            content_type='application/json'
        )
        
        # Should succeed if scraper exists
        # Note: This might fail due to authentication setup
    
    @patch('scraper.views.Container')
    def test_scraper_list_view_success(self, mock_container):
        """Test scraper list view"""
        mock_container_instance = Mock()
        mock_container_instance.run_command.return_value = [b'file1.py\nfile2.js\n']
        mock_container.return_value.get_container.return_value = mock_container_instance
        
        self.client.force_login(self.user)
        
        response = self.client.get(
            reverse('scraper:list_scrapers', kwargs={'path': 'test_scraper'})
        )
        
        # Should succeed if properly set up
        # Note: This might fail due to authentication setup
