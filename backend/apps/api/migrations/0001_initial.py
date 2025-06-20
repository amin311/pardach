# Generated by Django 4.2 on 2025-06-11 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=100, verbose_name='نام کلید')),
                ('key', models.CharField(max_length=64, unique=True, verbose_name='کلید')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضا')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='آخرین استفاده')),
                ('allowed_ips', models.TextField(blank=True, help_text='هر IP در یک خط', verbose_name='IP های مجاز')),
                ('rate_limit', models.PositiveIntegerField(default=1000, help_text='تعداد درخواست مجاز در روز', verbose_name='محدودیت تعداد درخواست')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'کلید API',
                'verbose_name_plural': 'کلیدهای API',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='APILog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE')], max_length=10, verbose_name='متد')),
                ('path', models.CharField(max_length=255, verbose_name='مسیر')),
                ('query_params', models.TextField(blank=True, verbose_name='پارامترهای درخواست')),
                ('request_body', models.TextField(blank=True, verbose_name='بدنه درخواست')),
                ('response_code', models.PositiveIntegerField(verbose_name='کد پاسخ')),
                ('response_body', models.TextField(blank=True, verbose_name='بدنه پاسخ')),
                ('ip_address', models.GenericIPAddressField(verbose_name='آدرس IP')),
                ('execution_time', models.FloatField(verbose_name='زمان اجرا (ثانیه)')),
                ('api_key', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to='api.apikey', verbose_name='کلید API')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='api_logs', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'لاگ API',
                'verbose_name_plural': 'لاگ\u200cهای API',
                'ordering': ['-created_at'],
            },
        ),
    ]
