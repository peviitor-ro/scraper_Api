from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from datetime import date
from .models import Source, Company, DataSet
from jobs.models import Job

User = get_user_model()


class SourceModelTest(TestCase):
    """Test cases for Source model"""
    
    def test_source_creation(self):
        """Test creating a source instance"""
        source = Source.objects.create(sursa='Test Source')
        self.assertEqual(source.sursa, 'Test Source')
        self.assertEqual(str(source), 'Test Source')
    
    def test_source_with_image(self):
        """Test creating a source with image"""
        # Create a simple test image file
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        source = Source.objects.create(
            sursa='Test Source',
            image=image_file
        )
        
        self.assertEqual(source.sursa, 'Test Source')
        self.assertTrue(source.image.name.startswith('images/'))
    
    def test_source_unique_constraint(self):
        """Test that source names must be unique"""
        Source.objects.create(sursa='Test Source')
        
        with self.assertRaises(Exception):
            Source.objects.create(sursa='Test Source')
    
    @patch('os.path.isfile')
    @patch('os.remove')
    def test_source_delete_removes_image(self, mock_remove, mock_isfile):
        """Test that deleting source removes associated image file"""
        mock_isfile.return_value = True
        
        source = Source.objects.create(sursa='Test Source')
        
        # Mock the image field
        mock_image = Mock()
        mock_image.path = '/fake/path/test.jpg'
        source.image = mock_image
        
        source.delete()
        
        mock_remove.assert_called_once_with('/fake/path/test.jpg')


class CompanyModelTest(TestCase):
    """Test cases for Company model"""
    
    def setUp(self):
        self.source = Source.objects.create(sursa='Test Source')
    
    def test_company_creation(self):
        """Test creating a company instance"""
        company = Company.objects.create(
            source=self.source,
            company='Test Company',
            scname='TC',
            website='https://testcompany.com',
            description='A test company'
        )
        
        self.assertEqual(company.source, self.source)
        self.assertEqual(company.company, 'Test Company')
        self.assertEqual(company.scname, 'TC')
        self.assertEqual(company.website, 'https://testcompany.com')
        self.assertEqual(company.description, 'A test company')
        self.assertEqual(str(company), 'Test Company')
    
    def test_company_without_source(self):
        """Test creating a company without source"""
        company = Company.objects.create(
            company='Test Company Without Source'
        )
        
        self.assertIsNone(company.source)
        self.assertEqual(company.company, 'Test Company Without Source')
    
    def test_company_delete_cascades_jobs(self):
        """Test that deleting company also deletes associated jobs"""
        company = Company.objects.create(
            source=self.source,
            company='Test Company'
        )
        
        # Create associated job
        job = Job.objects.create(
            company=company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer'
        )
        
        # Delete company should also delete job
        company.delete()
        
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(id=job.id)


class DataSetModelTest(TestCase):
    """Test cases for DataSet model"""
    
    def setUp(self):
        self.source = Source.objects.create(sursa='Test Source')
        self.company = Company.objects.create(
            source=self.source,
            company='Test Company'
        )
    
    def test_dataset_creation(self):
        """Test creating a dataset instance"""
        dataset = DataSet.objects.create(
            company=self.company,
            date=date.today(),
            data=100
        )
        
        self.assertEqual(dataset.company, self.company)
        self.assertEqual(dataset.date, date.today())
        self.assertEqual(dataset.data, 100)
        self.assertEqual(str(dataset), 'Test Company')
    
    def test_dataset_default_date(self):
        """Test dataset with default date"""
        dataset = DataSet.objects.create(
            company=self.company,
            data=50
        )
        
        self.assertIsInstance(dataset.date, date)


class CompanyViewsTest(APITestCase):
    """Test cases for Company views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.source = Source.objects.create(sursa='Test Source')
        self.company = Company.objects.create(
            source=self.source,
            company='Test Company'
        )
        self.user.company.add(self.company)
    
    def test_company_list_view(self):
        """Test company list API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual company list endpoint
        # Implementation depends on the actual view structure
    
    def test_company_detail_view(self):
        """Test company detail API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual company detail endpoint
        # Implementation depends on the actual view structure
    
    def test_company_create_view(self):
        """Test company creation API endpoint"""
        self.client.force_login(self.user)
        
        data = {
            'source': self.source.id,
            'company': 'New Test Company',
            'scname': 'NTC',
            'website': 'https://newtestcompany.com',
            'description': 'A new test company'
        }
        
        # This would test the actual company creation endpoint
        # Implementation depends on the actual view structure
    
    def test_company_update_view(self):
        """Test company update API endpoint"""
        self.client.force_login(self.user)
        
        data = {
            'company': 'Updated Test Company',
            'description': 'Updated description'
        }
        
        # This would test the actual company update endpoint
        # Implementation depends on the actual view structure
    
    def test_company_delete_view(self):
        """Test company deletion API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual company deletion endpoint
        # Implementation depends on the actual view structure
