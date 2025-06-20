# Generated by Django 4.2 on 2025-06-11 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('business', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام دسته\u200cبندی')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
            ],
            options={
                'verbose_name': 'دسته\u200cبندی اعلان',
                'verbose_name_plural': 'دسته\u200cبندی\u200cهای اعلان',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('type', models.CharField(choices=[('order_status', 'وضعیت سفارش'), ('payment_status', 'وضعیت پرداخت'), ('business_activity', 'فعالیت کسب\u200cوکار'), ('system', 'سیستمی'), ('user', 'کاربری'), ('message', 'پیام'), ('order', 'سفارش'), ('payment', 'پرداخت'), ('other', 'سایر')], max_length=20, verbose_name='نوع اعلان')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان')),
                ('content', models.TextField(verbose_name='محتوا')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده\u200cشده')),
                ('is_archived', models.BooleanField(default=False, verbose_name='آرشیو شده')),
                ('link', models.CharField(blank=True, max_length=255, verbose_name='لینک مرتبط')),
                ('priority', models.PositiveIntegerField(default=1, verbose_name='اولویت')),
                ('all_users', models.BooleanField(default=False, verbose_name='برای همه کاربران')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ خواندن')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='system_notifications', to='business.business', verbose_name='کسب\u200cوکار')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='notification.notificationcategory', verbose_name='دسته\u200cبندی')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'اعلان',
                'verbose_name_plural': 'اعلان\u200cها',
                'ordering': ['-created_at'],
            },
        ),
    ]
