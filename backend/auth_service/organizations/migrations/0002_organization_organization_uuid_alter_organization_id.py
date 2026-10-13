from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="organization_uuid",
            field=models.UUIDField(
                null=True,
                blank=True,
                editable=False,
            ),
        ),
    ]