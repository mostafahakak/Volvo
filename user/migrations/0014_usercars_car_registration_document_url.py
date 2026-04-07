# Generated manually for Firebase registration document URL

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_userrequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercars',
            name='car_registration_document_url',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
