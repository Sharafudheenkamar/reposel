from rest_framework import serializers
from .models import *

class Loginserializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = ('username', 'password','usertype')
class JournalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journals
        fields = ['user','pdfFile','name','title','viewOption']


class JournalsSerializerview(serializers.ModelSerializer):
    class Meta:
        model = Journals
        fields = ['user','pdfFile','name','title','image','viewOption']



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
# serializers.py
from rest_framework import serializers
from .models import Classroom

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'teacherid', 'name', 'capacity']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'  # Or specify fields like ['st_name', 'email', 'classs']

class ParentSerializer(serializers.ModelSerializer):
    parent_loginid=serializers.CharField(source='p_LID.id')
    class Meta:
        model = Parent
        fields = '__all__'

class StudentTaskCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studenttaskcompleted
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = Chat
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'sender_username', 'receiver_username']
class ChattedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = ['id', 'username', 'type']
class ChattedUsersSerializer1(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # Add a custom field for the name

    class Meta:
        model = Login
        fields = ['id', 'username', 'type', 'name']  # Include the custom name field

    def get_name(self, obj):
        # Fetch the related UserTable instance for the given LoginTable instance
        user = Teacher.objects.filter(LOGINID=obj).first()
        return user.name if user else None
    

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name', 't_LID']  # Include teacher's login ID (t_LID assumed)

class StudentMentorSerializer(serializers.ModelSerializer):
    mentors = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'st_name', 'email', 'mentors']

    def get_mentors(self, obj):
        classrooms = Classroom.objects.filter(students=obj)
        mentors = [classroom.teacherid for classroom in classrooms if classroom.teacherid]
        return TeacherSerializer(mentors, many=True).data