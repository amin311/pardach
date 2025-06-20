# Generated by Django 4.2 on 2025-06-11 07:44

import apps.templates_app.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('designs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=255, verbose_name='نام شرط')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('condition_type', models.CharField(choices=[('checkbox', 'چک\u200cباکس'), ('select', 'چند گزینه\u200cای'), ('radio', 'تک انتخابی'), ('color', 'انتخاب رنگ'), ('number', 'عدد'), ('text', 'متن')], max_length=20, verbose_name='نوع شرط')),
                ('options', models.TextField(blank=True, help_text='برای چند گزینه\u200cای، گزینه\u200cها را با کاما جدا کنید.', verbose_name='گزینه\u200cها')),
                ('default_value', models.CharField(blank=True, max_length=255, verbose_name='مقدار پیش\u200cفرض')),
                ('is_required', models.BooleanField(default=False, verbose_name='ضروری است')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('affects_pricing', models.BooleanField(default=False, verbose_name='تأثیر بر قیمت')),
                ('price_factor', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='ضریب قیمت')),
            ],
            options={
                'verbose_name': 'شرط',
                'verbose_name_plural': 'شرایط',
                'ordering': ['section', 'order'],
            },
        ),
        migrations.CreateModel(
            name='DesignInput',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='نام ورودی')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب ورودی')),
                ('is_required', models.BooleanField(default=True, verbose_name='ضروری است')),
                ('min_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداقل عرض')),
                ('min_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداقل ارتفاع')),
                ('max_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر عرض')),
                ('max_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر ارتفاع')),
                ('allowed_categories', models.ManyToManyField(blank=True, related_name='allowed_in_inputs', to='designs.designcategory', verbose_name='دسته\u200cبندی\u200cهای مجاز')),
                ('allowed_designs', models.ManyToManyField(blank=True, related_name='allowed_in_inputs', to='designs.design', verbose_name='طرح\u200cهای مجاز')),
                ('allowed_tags', models.ManyToManyField(blank=True, related_name='allowed_in_inputs', to='designs.tag', verbose_name='برچسب\u200cهای مجاز')),
                ('default_design', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='designs.design', verbose_name='طرح پیش\u200cفرض')),
            ],
            options={
                'verbose_name': 'ورودی طرح',
                'verbose_name_plural': 'ورودی\u200cهای طرح',
                'ordering': ['section', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=255, verbose_name='نام بخش')),
                ('slug', models.SlugField(blank=True, max_length=280, verbose_name='اسلاگ')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش بخش')),
                ('is_required', models.BooleanField(default=True, verbose_name='ضروری است')),
                ('unlimited_design_inputs', models.BooleanField(default=False, verbose_name='ورودی\u200cهای نامحدود طرح')),
                ('max_design_inputs', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر تعداد ورودی\u200cها')),
                ('preview_image', models.ImageField(blank=True, upload_to='sections/previews/', verbose_name='تصویر پیش\u200cنمایش')),
            ],
            options={
                'verbose_name': 'بخش',
                'verbose_name_plural': 'بخش\u200cها',
                'ordering': ['template', 'order'],
            },
        ),
        migrations.CreateModel(
            name='SetDimensions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=100, verbose_name='نام')),
                ('width', models.FloatField(verbose_name='عرض')),
                ('height', models.FloatField(verbose_name='ارتفاع')),
            ],
            options={
                'verbose_name': 'ابعاد ست',
                'verbose_name_plural': 'ابعاد ست\u200cها',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='thumbnails/', verbose_name='تصویر بندانگشتی')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='نام قالب')),
                ('slug', models.SlugField(blank=True, max_length=280, unique=True, verbose_name='اسلاگ')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات قالب')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='قیمت قالب')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='قیمت با تخفیف')),
                ('discount_percent', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='درصد تخفیف')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('featured', 'Featured'), ('archived', 'Archived')], default=apps.templates_app.models.Template.Status['DRAFT'], max_length=20, verbose_name='وضعیت')),
                ('is_premium', models.BooleanField(default=False, verbose_name='ویژه')),
                ('is_featured', models.BooleanField(default=False, verbose_name='برجسته')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')),
                ('usage_count', models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')),
                ('preview_image', models.ImageField(blank=True, upload_to='templates/previews/', verbose_name='تصویر پیش\u200cنمایش')),
                ('categories', models.ManyToManyField(blank=True, related_name='templates', to='designs.designcategory', verbose_name='دسته\u200cبندی\u200cها')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_templates', to=settings.AUTH_USER_MODEL, verbose_name='سازنده')),
                ('similar_templates', models.ManyToManyField(blank=True, to='templates_app.template', verbose_name='قالب\u200cهای مشابه')),
                ('tags', models.ManyToManyField(blank=True, related_name='templates', to='designs.tag', verbose_name='برچسب\u200cها')),
            ],
            options={
                'verbose_name': 'قالب',
                'verbose_name_plural': 'قالب\u200cها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='نام پروژه')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('is_completed', models.BooleanField(default=False, verbose_name='تکمیل شده')),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='قیمت نهایی')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='شناسه یکتا')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_templates', to='templates_app.template', verbose_name='قالب')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_templates', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'قالب کاربر',
                'verbose_name_plural': 'قالب\u200cهای کاربر',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('is_completed', models.BooleanField(default=False, verbose_name='تکمیل شده')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_sections', to='templates_app.section', verbose_name='بخش')),
                ('user_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_sections', to='templates_app.usertemplate', verbose_name='قالب کاربر')),
            ],
            options={
                'verbose_name': 'بخش کاربر',
                'verbose_name_plural': 'بخش\u200cهای کاربر',
                'ordering': ['section__order'],
            },
        ),
        migrations.CreateModel(
            name='UserDesignInput',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('order', models.PositiveIntegerField(verbose_name='ترتیب ورودی')),
                ('design', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='designs.design', verbose_name='طرح انتخابی')),
                ('design_input', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='templates_app.designinput', verbose_name='ورودی طرح اصلی')),
                ('user_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_design_inputs', to='templates_app.usersection', verbose_name='بخش کاربر')),
            ],
            options={
                'verbose_name': 'ورودی طرح کاربر',
                'verbose_name_plural': 'ورودی\u200cهای طرح کاربر',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='UserCondition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('value', models.CharField(blank=True, max_length=255, verbose_name='مقدار انتخابی')),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='templates_app.condition', verbose_name='شرط اصلی')),
                ('user_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_conditions', to='templates_app.usersection', verbose_name='بخش کاربر')),
            ],
            options={
                'verbose_name': 'شرط کاربر',
                'verbose_name_plural': 'شرایط کاربر',
                'ordering': ['condition__order'],
            },
        ),
        migrations.AddField(
            model_name='section',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='templates_app.template', verbose_name='قالب'),
        ),
        migrations.AddField(
            model_name='designinput',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='design_inputs', to='templates_app.section', verbose_name='بخش'),
        ),
        migrations.AddField(
            model_name='condition',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='templates_app.section', verbose_name='بخش'),
        ),
        migrations.CreateModel(
            name='SectionRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='شناسه')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='آخرین بروزرسانی')),
                ('name', models.CharField(max_length=100, verbose_name='نام قانون')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('min_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداقل عرض')),
                ('max_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر عرض')),
                ('min_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداقل ارتفاع')),
                ('max_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر ارتفاع')),
                ('min_dpi', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداقل DPI')),
                ('allowed_design_types', models.CharField(blank=True, help_text='انواع طرح مجاز با کاما جدا شوند', max_length=255, verbose_name='انواع طرح مجاز')),
                ('allowed_file_types', models.CharField(blank=True, help_text='پسوندهای مجاز با کاما جدا شوند', max_length=255, verbose_name='فرمت\u200cهای فایل مجاز')),
                ('max_file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='حداکثر حجم فایل (KB)')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='templates_app.section', verbose_name='بخش')),
            ],
            options={
                'verbose_name': 'قانون بخش',
                'verbose_name_plural': 'قوانین بخش',
                'ordering': ['section', 'name'],
                'unique_together': {('section', 'name')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('template', 'slug')},
        ),
    ]
