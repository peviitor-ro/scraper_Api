from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from .models import City

class CitySerializer(serializers.Serializer):
    class Meta:
        model = City
        fields = ['name', 'county__name', 'county__abreviate']

    def to_representation(self, instance):
        return {
            'name': instance.name,
            'county': instance.county.name,
            'abreviate': instance.county.abreviate
        }


    
