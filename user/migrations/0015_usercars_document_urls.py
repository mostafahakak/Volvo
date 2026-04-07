# Split registration URL into front/back + driver license URLs

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_usercars_car_registration_document_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercars',
            old_name='car_registration_document_url',
            new_name='car_registration_front_url',
        ),
        migrations.AddField(
            model_name='usercars',
            name='car_registration_back_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='usercars',
            name='driver_license_front_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='usercars',
            name='driver_license_back_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
