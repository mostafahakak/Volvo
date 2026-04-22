from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0022_maintenanceschedule_car_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitecontactsettings",
            name="app_theme_default",
            field=models.CharField(
                default="light",
                help_text="light, dark, or system",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="sitecontactsettings",
            name="user_can_change_theme",
            field=models.BooleanField(
                default=True,
                help_text="If false, the app always uses app_theme_default.",
            ),
        ),
        migrations.AddField(
            model_name="sitecontactsettings",
            name="new_user_default_points",
            field=models.IntegerField(
                default=20,
                help_text="Starting points balance and history for new app accounts.",
            ),
        ),
    ]
