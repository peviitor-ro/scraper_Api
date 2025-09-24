from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import County, City

User = get_user_model()


class CountyModelTest(TestCase):
    """Test cases for County model"""
    
    def test_county_creation(self):
        """Test creating a county instance"""
        county = County.objects.create(
            name='Bucuresti',
            abreviate='B',
            municipality='Bucuresti'
        )
        
        self.assertEqual(county.name, 'Bucuresti')
        self.assertEqual(county.abreviate, 'B')
        self.assertEqual(county.municipality, 'Bucuresti')
        self.assertEqual(str(county), 'Bucuresti')
    
    def test_county_abbreviation_unique(self):
        """Test that county abbreviation must be unique"""
        County.objects.create(
            name='Bucuresti',
            abreviate='B',
            municipality='Bucuresti'
        )
        
        with self.assertRaises(Exception):
            County.objects.create(
                name='Another County',
                abreviate='B',  # Same abbreviation
                municipality='Another Municipality'
            )


class CityModelTest(TestCase):
    """Test cases for City model"""
    
    def setUp(self):
        self.county = County.objects.create(
            name='Bucuresti',
            abreviate='B',
            municipality='Bucuresti'
        )
    
    def test_city_creation(self):
        """Test creating a city instance"""
        city = City.objects.create(
            name='Sector 1',
            county=self.county
        )
        
        self.assertEqual(city.name, 'Sector 1')
        self.assertEqual(city.county, self.county)
        self.assertEqual(str(city), 'Sector 1')
    
    def test_city_county_relationship(self):
        """Test the city-county relationship"""
        city1 = City.objects.create(name='Sector 1', county=self.county)
        city2 = City.objects.create(name='Sector 2', county=self.county)
        
        # Test reverse relationship
        cities = self.county.cities.all()
        self.assertIn(city1, cities)
        self.assertIn(city2, cities)
        self.assertEqual(cities.count(), 2)
    
    def test_city_cascade_delete(self):
        """Test that deleting county cascades to cities"""
        city = City.objects.create(name='Test City', county=self.county)
        
        self.county.delete()
        
        with self.assertRaises(City.DoesNotExist):
            City.objects.get(id=city.id)


class OraseViewsTest(APITestCase):
    """Test cases for County and City views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test data
        self.county = County.objects.create(
            name='Bucuresti',
            abreviate='B',
            municipality='Bucuresti'
        )
        self.city = City.objects.create(
            name='Sector 1',
            county=self.county
        )
    
    def test_county_list_view(self):
        """Test county list API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual county list endpoint
        # Implementation depends on the actual view structure
        # Typically would be something like:
        # response = self.client.get(reverse('orase:county-list'))
        # self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Bucuresti')
    
    def test_city_list_view(self):
        """Test city list API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual city list endpoint
        # Implementation depends on the actual view structure
    
    def test_cities_by_county_view(self):
        """Test getting cities by county"""
        self.client.force_login(self.user)
        
        # This would test getting cities for a specific county
        # Implementation depends on the actual view structure
    
    def test_county_detail_view(self):
        """Test county detail API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual county detail endpoint
        # Implementation depends on the actual view structure
    
    def test_city_detail_view(self):
        """Test city detail API endpoint"""
        self.client.force_login(self.user)
        
        # This would test the actual city detail endpoint
        # Implementation depends on the actual view structure
