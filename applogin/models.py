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

# Create your models here.
USER_TYPE_CHOICES = {
    ("ADMIN","Admin"),
    ("INSTITUTE","Institute"),
    ("TEACHER","Teacher"),
    ("STUDENT","Student"),

}
STATUS_CHOICES = {
    ("ACTIVE","Active"),
    ("DEACTIVE","Deactive"),
}
class Userprofile(AbstractUser):
    #username
    #password
    #first_name
    #email
    name=models.CharField(max_length=100,null=False,blank=True)
    profile_image = models.ImageField(null=True,blank=True,upload_to='studentimages')
    phone_number=models.CharField(max_length=100,null=False,blank=True)
    stream=models.CharField(max_length=100,null=False,blank=True)
    year=models.CharField(max_length=100,null=False,blank=True)
    status =  models.CharField(max_length=20,null=False,choices=STATUS_CHOICES)
    is_active = models.BooleanField(max_length=20,null=False,default=True)
    user_type = models.CharField(max_length=20,null=False,choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Token(models.Model):
    key = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(
        Userprofile,
        related_name="auth_tokens",
        on_delete=models.CASCADE,
        verbose_name="user",
        unique=True,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    session_dict = models.TextField(null=False, default="{}")

    dict_ready = False
    data_dict = None

    def _init_(self, *args, **kwargs):
        self.dict_ready = False
        self.data_dict = None
        super(Token, self)._init_(*args, **kwargs)

    def generate_key(self):
        return "".join(
            random.choice(
                string.ascii_lowercase + string.digits + string.ascii_uppercase
            )
            for i in range(40)
        )

    def save(self, *args, **kwargs):
        if not self.key:
            new_key = self.generate_key()
            while type(self).objects.filter(key=new_key).exists():
                new_key = self.generate_key()
            self.key = new_key
        return super(Token, self).save(*args, **kwargs)

    def read_session(self):
        if self.session_dict == "null":
            self.data_dict = {}
        else:
            self.data_dict = json.loads(self.session_dict)
        self.dict_ready = True

    def update_session(self, tdict, save=True, clear=False):
        if not clear and not self.dict_ready:
            self.read_session()
        if clear:
            self.data_dict = tdict
            self.dict_ready = True
        else:
            for key, value in tdict.items():
                self.data_dict[key] = value
        if save:
            self.write_back()

    def set(self, key, value, save=True):
        if not self.dict_ready:
            self.read_session()
        self.data_dict[key] = value
        if save:
            self.write_back()

    def write_back(self):
        self.session_dict = json.dumps(self.data_dict)
        self.save()

    def get(self, key, default=None):
        if not self.dict_ready:
            self.read_session()
        return self.data_dict.get(key, default)

    def _str_(self):
        return str(self.user) if self.user else str(self.id)

class Journals(models.Model):
    user=models.ForeignKey(Userprofile,on_delete=models.CASCADE,null=True,blank=True)
    image = models.ImageField(null=True,blank=True,upload_to='pdfthumbnail')
    pdfFile = models.FileField(null=True,blank=True,upload_to='pdfFile')
    name=models.CharField(max_length=100,null=False,blank=True)
    title=models.CharField(max_length=100,null=False,blank=True)
    viewOption=models.CharField(max_length=100,null=False,blank=True)

  


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

