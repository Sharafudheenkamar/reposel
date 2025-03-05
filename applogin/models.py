from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
import json
from pdf2image import convert_from_path
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from pdf2image import convert_from_path
from io import BytesIO
import os
from django.core.files.base import ContentFile

class Login(models.Model):

  username = models.CharField(max_length=255,null=True,blank=True)
  password= models.CharField(max_length=255,null=True,blank=True)
  usertype=models.CharField(max_length=255,null=True,blank=True)


class Teacher(models.Model):
   t_name=models.CharField(max_length=255,null=True,blank=True)
   email=models.CharField(max_length=255,null=True,blank=True)
   p_phno=models.BigIntegerField(null=True,blank=True)
   qualification=models.CharField(max_length=255,null=True,blank=True)
   subject=models.CharField(max_length=255,null=True,blank=True)
   experience=models.BigIntegerField(null=True,blank=True)
   t_LID=models.ForeignKey(Login,on_delete=models.CASCADE,null=True,blank=True)



class Student(models.Model):
  st_name=models.CharField(max_length=255,null=True,blank=True)
  classs=models.CharField(max_length=255,null=True,blank=True)
  stream=models.CharField(max_length=255,null=True,blank=True)
  email=models.CharField(max_length=255,null=True,blank=True)
  st_phno=models.BigIntegerField(null=True,blank=True)
  st_LID=models.ForeignKey(Login,on_delete=models.CASCADE,null=True,blank=True)
#   classroomid=models.ManyToManyField(Classroom,on_delete=models.CASCADE,null=True,blank=True)
  selscore=models.FloatField(null=True,blank=True)

class Classroom(models.Model):
    teacherid=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    students= models.ManyToManyField(Student)

class Parent(models.Model):
   p_name=models.CharField(max_length=255,null=True,blank=True)
   email=models.CharField(max_length=255,null=True,blank=True)
   p_phno=models.BigIntegerField(null=True,blank=True)
   relation=models.CharField(max_length=255,null=True,blank=True)
   p_LID=models.ForeignKey(Login,on_delete=models.CASCADE,null=True,blank=True)
   student_id=models.ManyToManyField(Student,blank=True)



   


class Journals(models.Model):
    user=models.ForeignKey(Login,on_delete=models.CASCADE,null=True,blank=True)
    image = models.ImageField(null=True,blank=True,upload_to='pdfthumbnail')
    pdfFile = models.FileField(null=True,blank=True,upload_to='pdfFile')
    name=models.CharField(max_length=100,null=False,blank=True)
    title=models.CharField(max_length=100,null=False,blank=True)
    viewOption=models.CharField(max_length=100,null=False,blank=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now=True,null=True,blank=True)


  


    def save(self, *args, **kwargs):
            # Check if the instance is new or updated
            is_new = self.pk is None

            # Save the instance initially
            super().save(*args, **kwargs)

            # Generate a thumbnail only if a new PDF is uploaded and no image exists
            if self.pdfFile and not self.image and is_new:
                try:
                    # Convert the first page of the PDF to an image
                    pdf_path = self.pdfFile.path
                    images = convert_from_path(pdf_path, first_page=1, last_page=1)
                    if images:
                        first_page_image = images[0]

                        # Resize the image (optional)
                        first_page_image.thumbnail((300, 300), Image.Resampling.LANCZOS)

                        # Save the image in JPEG format
                        image_io = BytesIO()
                        first_page_image.save(image_io, format='JPEG', quality=100) 
                        print(first_page_image) # Save as JPEG with quality 85

                        # Save the JPEG image to the `image` field
                        self.image.save(
                            os.path.basename(pdf_path).replace('.pdf', '_thumbnail.jpg'),
                            ContentFile(image_io.getvalue()),
                            save=False  # Avoid infinite recursion
                        )

                        # Save the instance again to store the image
                        super().save(update_fields=['image'])  # Only update the `image` field
                except Exception as e:
                    print(f"Error generating thumbnail: {e}")
                
from django.db import models
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response

# Models


class Task(models.Model):
    teacherid=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='tasks')

class Studenttask(models.Model):
    studentid=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
    taskid=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    taskfile=models.FileField(upload_to='studentcompletedtask',null=True,blank=True)
    taskdescription=models.CharField(max_length=100,null=True,blank=True)
    taskmarks=models.IntegerField(null=True,blank=True)
    taskstatus=models.CharField(max_length=100,null=True,blank=True)
class Studenttaskcompleted(models.Model):
    studentid=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
    taskid=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    taskfile=models.FileField(upload_to='studentcompletedtask',null=True,blank=True)
    taskdescription=models.CharField(max_length=100,null=True,blank=True)
    taskmarks=models.IntegerField(null=True,blank=True)
    taskstatus=models.CharField(max_length=100,null=True,blank=True)

class Studentclass:
    studentid=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
    classroomid=models.ForeignKey(Classroom,on_delete=models.CASCADE,null=True,blank=True)
    studentstatus=models.CharField(max_length=100,null=True,blank=True)
    

from django.db import models

class ChatHistory(models.Model):

    user_query = models.TextField()  # User's query
    chatbot_response = models.TextField()  # Chatbot's response
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the interaction

    def _str_(self):
        return f"Chat at {self.timestamp}"
    


class Chat(models.Model):
    sender = models.ForeignKey(
        'Login', 
        related_name='sent_messages', 
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        'Login', 
        related_name='received_messages', 
        on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"From {self.sender.username} to {self.receiver.username}"
    

class Notifications(models.Model):
    userid=models.ForeignKey(Login,on_delete=models.CASCADE,null=True,blank=True)
    notification=models.CharField(max_length=100,null=True,blank=True)
    notification_date=models.DateField(auto_now=True,blank=True,null=True)