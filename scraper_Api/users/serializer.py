from rest_framework import serializers
from .models import CustomUser
from jobs.models import Company
from scraper.models import Scraper
from rest_framework.response import Response

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['email']

    def save(self, **kwargs):
        if CustomUser.objects.filter(email=self.validated_data['email']).exists():
            return CustomUser.objects.get(email=self.validated_data['email'])
        return super().save(**kwargs)

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)
    
class UserUpdateSerializer(serializers.Serializer): 
    companies = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['email', 'companies']  
    def update(self, data):
        
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        
        user = CustomUser.objects.get(email=data['email'])
        for key, value in data.items():
            if hasattr(user, key):
                if key == 'company':
                    companies = Company.objects.filter(company__in=value)
                    user.company.set(companies)
                elif key == 'scraper':
                    scrapers = Scraper.objects.filter(name__in=value)
                    user.scraper.set(scrapers)
                else:
                    setattr(user, key, value)
        user.save()
    
        return Response({'message': 'User updated'}, status=200)
 
    def get_companies(self, obj):
        return obj.company.all().values('company')



    


