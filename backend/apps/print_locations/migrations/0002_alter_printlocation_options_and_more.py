# Generated by Django 4.2 on 2025-06-04 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_locations', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='printlocation',
            options={'ordering': ['city', 'name'], 'verbose_name': 'مکان چاپ', 'verbose_name_plural': 'مکان\u200cهای چاپ'},
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='description',
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='max_height',
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='max_width',
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='min_dpi',
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='supports_digital',
        ),
        migrations.RemoveField(
            model_name='printlocation',
            name='supports_manual',
        ),
        migrations.AddField(
            model_name='printlocation',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='آدرس'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='شهر'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100, verbose_name='شخص رابط'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='ایمیل'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='عرض جغرافیایی'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='طول جغرافیایی'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='opening_hours',
            field=models.CharField(blank=True, max_length=200, verbose_name='ساعت کاری'),
        ),
        migrations.AddField(
            model_name='printlocation',
            name='phone',
            field=models.CharField(blank=True, max_length=15, verbose_name='تلفن'),
        ),
        migrations.AlterField(
            model_name='printlocation',
            name='name',
            field=models.CharField(max_length=100, verbose_name='نام مکان'),
        ),
    ]
