# Generated by Django 5.0.2 on 2024-03-04 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_rename_profilepicurl_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='image/avatar'),
        ),
    ]