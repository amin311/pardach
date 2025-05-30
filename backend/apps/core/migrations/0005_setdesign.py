# Generated by Django 4.2 on 2025-05-03 21:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_order_orderstage_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='SetDesign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('design_file', models.FileField(upload_to='designs/', verbose_name='فایل طراحی')),
                ('preview', models.ImageField(blank=True, null=True, upload_to='design_previews/', verbose_name='پیش\u200cنمایش')),
                ('status', models.CharField(choices=[('SUBMITTED', 'Submitted'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='SUBMITTED', max_length=10, verbose_name='وضعیت')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ به\u200cروزرسانی')),
                ('designer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setdesigns', to=settings.AUTH_USER_MODEL)),
                ('order_stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='designs', to='core.orderstage')),
            ],
            options={
                'verbose_name': 'طراحی ست',
                'verbose_name_plural': 'طراحی\u200cهای ست',
                'ordering': ['-created_at'],
            },
        ),
    ]
