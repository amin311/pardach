from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('print_locations', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PrintLocation',
        ),
    ] 