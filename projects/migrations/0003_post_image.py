# Generated by Django 5.0.2 on 2024-02-19 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_profile_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/profile/'),
        ),
    ]
