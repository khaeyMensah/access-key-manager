# Generated by Django 5.0.6 on 2024-07-18 18:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('access_keys', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='accesskey',
            name='assigned_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accesskey',
            name='revoked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revoked_access_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accesskey',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_keys', to='users.school'),
        ),
        migrations.AddField(
            model_name='keylog',
            name='access_key',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='key_logs', to='access_keys.accesskey'),
        ),
        migrations.AddField(
            model_name='keylog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
