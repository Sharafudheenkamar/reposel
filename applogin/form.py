from django import forms
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['t_name', 'email', 'p_phno', 'qualification', 'subject', 'experience']
