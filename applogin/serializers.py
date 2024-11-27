from rest_framework import serializers
from .models import Userprofile,Journals

class UserprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['name','stream','year','username','phone_number','password','profile_image']

        extra_kwargs = {
            'password': {'write_only': True},  # Prevent password from being returned in the response
        }

    def create(self, validated_data):
        # Remove the raw password from validated_data
        password = validated_data.pop('password')
        # Create the user instance without saving it
        user = Userprofile(**validated_data)
        # Hash the password
        user.set_password(password)
        # Save the user instance
        user.save()
        return user
class JournalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journals
        fields = ['user','pdfFile','name','title','viewOption']


class JournalsSerializerview(serializers.ModelSerializer):
    class Meta:
        model = Journals
        fields = ['user','pdfFile','name','title','image','viewOption']

    