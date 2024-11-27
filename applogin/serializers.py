from rest_framework import serializers
from .models import Userprofile

class UserprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['name','stream','year','username','phone_number','password','profile_image']
