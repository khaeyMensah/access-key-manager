# Generated by Django 5.0.6 on 2024-06-27 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_keys', '0005_alter_accesskey_expiry_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesskey',
            name='expiry_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='accesskey',
            name='procurement_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
