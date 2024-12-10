# Generated by Django 5.1.3 on 2024-12-10 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applogin', '0008_alter_journals_created_at_alter_journals_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('DEACTIVE', 'Deactive')], max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.CharField(choices=[('STUDENT', 'Student'), ('INSTITUTE', 'Institute'), ('TEACHER', 'Teacher'), ('ADMIN', 'Admin')], max_length=20),
        ),
        migrations.DeleteModel(
            name='Journals1',
        ),
    ]