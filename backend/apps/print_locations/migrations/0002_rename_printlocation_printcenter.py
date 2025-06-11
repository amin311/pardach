from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('print_locations', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PrintLocation',
            new_name='PrintCenter',
        ),
    ]
