# Generated by Django 3.2.9 on 2021-11-08 05:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_auto_20211105_0654'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='url_id',
            field=models.UUIDField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='phone',
            field=models.CharField(default='None', max_length=25, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
