from rest_framework import serializers
from .models import CustomUser


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
    


