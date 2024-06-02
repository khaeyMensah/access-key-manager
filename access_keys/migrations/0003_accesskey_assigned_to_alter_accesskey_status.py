# Generated by Django 5.0.6 on 2024-06-02 12:35

import access_keys.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_keys', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='accesskey',
            name='assigned_to',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='access_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='accesskey',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked')], max_length=10, validators=[access_keys.models.validate_active_key]),
        ),
    ]
