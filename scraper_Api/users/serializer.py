from rest_framework import serializers
from .models import CustomUser
from validator.models import Company
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
    def update(self, data):
        
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        
        user = CustomUser.objects.get(email=data['email'])
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        try:
            companies = Company.objects.all() 
            user.company.set(companies)
        except Exception as e:
            return Response({'error': 'Error adding companies to user'}, status=400)
        
        user.save()

        return Response(status=201)

    


