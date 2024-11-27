from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
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

