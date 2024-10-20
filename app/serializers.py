from rest_framework import serializers
from .models import Calendar

class CropCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ['id', 'name', 'planted_date', 'harvested_date', 'earn', 'expense']  # Add your fields here
