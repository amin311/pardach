# Generated by Django 4.2 on 2025-06-11 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='عنوان چت')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chats', to='business.business', verbose_name='کسب\u200cوکار')),
                ('participants', models.ManyToManyField(related_name='chats', to=settings.AUTH_USER_MODEL, verbose_name='شرکت\u200cکنندگان')),
            ],
            options={
                'verbose_name': 'چت',
                'verbose_name_plural': 'چت\u200cها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
                ('type', models.CharField(choices=[('order_status', 'وضعیت سفارش'), ('payment_status', 'وضعیت پرداخت'), ('business_activity', 'فعالیت کسب\u200cوکار'), ('general', 'عمومی')], max_length=20, verbose_name='نوع اعلان')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان')),
                ('content', models.TextField(verbose_name='محتوا')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده\u200cشده')),
                ('link', models.CharField(blank=True, max_length=255, verbose_name='لینک مرتبط')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comm_notifications', to='business.business', verbose_name='کسب\u200cوکار')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comm_notifications', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'اعلان',
                'verbose_name_plural': 'اعلان\u200cها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
                ('content', models.TextField(verbose_name='محتوای پیام')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده\u200cشده')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='communication.chat', verbose_name='چت')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='فرستنده')),
            ],
            options={
                'verbose_name': 'پیام',
                'verbose_name_plural': 'پیام\u200cها',
                'ordering': ['created_at'],
            },
        ),
    ]
