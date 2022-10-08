from .models import Buildings,Buildingaccess
from rest_framework import serializers 
from datetime import datetime

class BuildingRegisterSerializer(serializers.ModelSerializer):
    access_timestamp = serializers.DateTimeField(default=datetime.now())
    class Meta:
        model = Buildingaccess
        fields = '__all__'
