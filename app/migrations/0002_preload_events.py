from django.db import migrations

def preload_events(apps, schema_editor):
    Event = apps.get_model('app', 'Event')

    events = [
        # OFF STAGE
        dict(name="Short Story", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Poetry Writing", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Essay Writing", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Speech", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Pencil Drawing", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Watercolor Painting", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Poster / Cartoon Drawing", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Photography", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Mehendi", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Cinema Review", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Face Painting", stage_type="OFF_STAGE", event_type="DUO", min_team_size=2, max_team_size=2),
        dict(name="Micro Story / Flash Fiction", stage_type="OFF_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Short Film", stage_type="OFF_STAGE", event_type="GROUP", min_team_size=10, max_team_size=15),

        

        # ON STAGE SINGLE
        dict(name="Light Music", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Classical Music", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Western Music", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Folk Dance", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Classical Dance", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Semi-Classical Dance", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Cinematic Dance", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Mono Act", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),
        dict(name="Poem Recitation", stage_type="ON_STAGE", event_type="SINGLE", min_team_size=1, max_team_size=1),


        # ON STAGE GROUP
        dict(name="Group Song", stage_type="ON_STAGE", event_type="GROUP", min_team_size=2, max_team_size=10),
        dict(name="Folk Song", stage_type="ON_STAGE", event_type="GROUP", min_team_size=2, max_team_size=10),
        dict(name="Western Music (Group)", stage_type="ON_STAGE", event_type="GROUP", min_team_size=2, max_team_size=10),
        dict(name="Folk Dance (Group)", stage_type="ON_STAGE", event_type="GROUP", min_team_size=2, max_team_size=10),
        dict(name="Semi-Classical Dance (Group)", stage_type="ON_STAGE", event_type="GROUP", min_team_size=2, max_team_size=10),
        dict(name="Cinematic Dance (Group)", stage_type="ON_STAGE", event_type="GROUP", min_team_size=7, max_team_size=7),
        dict(name="Oppana", stage_type="ON_STAGE", event_type="GROUP", min_team_size=10, max_team_size=10),
        dict(name="Thiruvathira", stage_type="ON_STAGE", event_type="GROUP", min_team_size=8, max_team_size=12),
        dict(name="Drama / Play", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=12),
        dict(name="Tablo", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=10),
        dict(name="Mime", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=6),
        dict(name="Mappila Song", stage_type="ON_STAGE", event_type="GROUP", min_team_size=6, max_team_size=6),

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
