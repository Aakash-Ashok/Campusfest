from django.db import migrations

def preload_events(apps, schema_editor):
    Event = apps.get_model('app', 'Event')

    events = [
        # OFF STAGE
        dict(name="Cherukatha", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Kavitha Rachana", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Photography", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Face Painting", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Short Film", stage_type="OFF_STAGE", event_type="GROUP", min_team_size=10, max_team_size=15),

        # ON STAGE SINGLE
        dict(name="Light Music", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Mono Act", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),

        # ON STAGE GROUP
        dict(name="Drama", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=12),
        dict(name="Group Dance (Cine)", stage_type="ON_STAGE", event_type="GROUP", min_team_size=7, max_team_size=7),
        dict(name="Mime", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=6),
        dict(name="Oppana", stage_type="ON_STAGE", event_type="GROUP", min_team_size=10, max_team_size=10),
    ]

    for event in events:
        Event.objects.get_or_create(
            name=event["name"],
            defaults=event
        )

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(preload_events),
    ]
