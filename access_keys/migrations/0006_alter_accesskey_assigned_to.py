# Generated by Django 5.0.6 on 2024-06-04 05:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_keys', '0005_remove_accesskey_purchased'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesskey',
            name='assigned_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_keys', to=settings.AUTH_USER_MODEL),
        ),
    ]