# Generated by Django 5.0.6 on 2024-06-18 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
