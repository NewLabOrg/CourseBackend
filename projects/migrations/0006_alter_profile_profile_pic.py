# Generated by Django 5.0.2 on 2024-03-03 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_news_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]