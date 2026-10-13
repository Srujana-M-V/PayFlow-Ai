import uuid

from django.db import migrations


def populate_organization_uuids(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    database = schema_editor.connection.alias

    for organization in Organization.objects.using(database).filter(
        organization_uuid__isnull=True
    ).iterator():
        organization.organization_uuid = uuid.uuid4()
        organization.save(
            using=database,
            update_fields=["organization_uuid"],
        )


class Migration(migrations.Migration):

    dependencies = [
    ("organizations", "0003_alter_organization_organization_uuid"),
]

    operations = [
        migrations.RunPython(
            populate_organization_uuids,
            migrations.RunPython.noop,
        ),
    ]