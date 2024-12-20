# Generated by Django 5.1.3 on 2024-11-27 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applogin', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='photo',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='studentimages'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stream',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='year',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.CharField(choices=[('TEACHER', 'Teacher'), ('INSTITUTE', 'Institute'), ('ADMIN', 'Admin')], max_length=20),
        ),
    ]
