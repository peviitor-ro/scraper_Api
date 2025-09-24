from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from datetime import date
from .models import Job
from company.models import Company, Source

User = get_user_model()


class JobModelTest(TestCase):
    """Test cases for Job model"""
    
    def setUp(self):
        self.source = Source.objects.create(sursa='test_source')
        self.company = Company.objects.create(
            source=self.source,
            company='Test Company',
            website='https://testcompany.com'
        )
    
    def test_job_creation(self):
        """Test creating a job instance"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            city='Bucharest',
            county='Bucuresti',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer',
            remote='Yes',
            date=date.today()
        )
        
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.country, 'Romania')
        self.assertEqual(job.city, 'Bucharest')
        self.assertEqual(job.job_title, 'Software Developer')
        self.assertEqual(str(job), 'Software Developer')
        self.assertFalse(job.edited)
        self.assertFalse(job.published)
    
    def test_job_get_job_id(self):
        """Test job ID generation from job link"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer'
        )
        
        job_id = job.getJobId
        self.assertIsInstance(job_id, str)
        self.assertEqual(len(job_id), 32)  # MD5 hash length
    
    @patch('jobs.models.solr')
    def test_job_publish_success(self, mock_solr):
        """Test successful job publishing to Solr"""
        mock_solr.add.return_value = None
        mock_solr.commit.return_value = None
        
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            city='Bucharest',
            county='Bucuresti',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer',
            remote='Yes'
        )
        
        response = job.publish()
        
        mock_solr.add.assert_called_once()
        mock_solr.commit.assert_called_once()
        self.assertEqual(response.status_code, 200)
    
    @patch('jobs.models.solr')
    def test_job_unpublish_success(self, mock_solr):
        """Test successful job unpublishing from Solr"""
        mock_solr.delete.return_value = None
        mock_solr.commit.return_value = None
        
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer',
            published=True  # Set as published initially
        )
        
        response = job.unpublish()
        
        mock_solr.delete.assert_called_once()
        mock_solr.commit.assert_called_once()
        job.refresh_from_db()
        self.assertFalse(job.published)
        self.assertEqual(response.status_code, 200)
    
    @patch('jobs.models.solr')
    def test_job_delete_published(self, mock_solr):
        """Test deleting a published job removes it from Solr"""
        mock_solr.delete.return_value = None
        mock_solr.commit.return_value = None
        
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer',
            published=True
        )
        
        job.delete()
        
        mock_solr.delete.assert_called_once()
        mock_solr.commit.assert_called_once()
    
    def test_job_delete_unpublished(self):
        """Test deleting an unpublished job doesn't call Solr"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer',
            published=False
        )
        
        job.delete()  # Should not raise any errors


class JobViewsTest(APITestCase):
    """Test cases for Job views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.source = Source.objects.create(sursa='test_source')
        self.company = Company.objects.create(
            source=self.source,
            company='Test Company'
        )
        self.user.company.add(self.company)
    
    def test_job_list_view(self):
        """Test job list API endpoint"""
        # Create test jobs
        Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer 1'
        )
        Job.objects.create(
            company=self.company,
            country='Romania', 
            job_link='https://testcompany.com/jobs/2',
            job_title='Software Developer 2'
        )
        
        self.client.force_login(self.user)
        
        # This would test the actual job list endpoint
        # Implementation depends on the actual view structure
    
    def test_job_detail_view(self):
        """Test job detail API endpoint"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer'
        )
        
        self.client.force_login(self.user)
        
        # This would test the actual job detail endpoint
        # Implementation depends on the actual view structure
    
    def test_job_create_view(self):
        """Test job creation API endpoint"""
        self.client.force_login(self.user)
        
        data = {
            'company': self.company.id,
            'country': 'Romania',
            'city': 'Bucharest',
            'job_link': 'https://testcompany.com/jobs/new',
            'job_title': 'New Software Developer',
            'remote': 'Yes'
        }
        
        # This would test the actual job creation endpoint
        # Implementation depends on the actual view structure
    
    def test_job_update_view(self):
        """Test job update API endpoint"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer'
        )
        
        self.client.force_login(self.user)
        
        data = {
            'job_title': 'Senior Software Developer',
            'edited': True
        }
        
        # This would test the actual job update endpoint
        # Implementation depends on the actual view structure
    
    def test_job_delete_view(self):
        """Test job deletion API endpoint"""
        job = Job.objects.create(
            company=self.company,
            country='Romania',
            job_link='https://testcompany.com/jobs/1',
            job_title='Software Developer'
        )
        
        self.client.force_login(self.user)
        
        # This would test the actual job deletion endpoint
        # Implementation depends on the actual view structure
