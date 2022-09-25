from .models import (
    Users, 
    Closecontacts, 
    Infectionhistory,
    Notifications
    )
from rest_framework import exceptions, serializers 

class CloseContactSerializer(serializers.ModelSerializer):
    """Handle serialization and deserialization of CloseContact objects."""

    class Meta:
        model = Closecontacts
        fields = '__all__'
    
