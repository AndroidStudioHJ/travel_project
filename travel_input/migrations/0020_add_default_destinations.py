from django.db import migrations

def add_default_destinations(apps, schema_editor):
    Destination = apps.get_model('travel_input', 'Destination')
    destinations = [
        '서울', '부산', '인천', '대구', '대전', '광주', '울산', '세종',
        '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
    ]
    for destination in destinations:
        Destination.objects.get_or_create(name=destination)

def remove_default_destinations(apps, schema_editor):
    Destination = apps.get_model('travel_input', 'Destination')
    Destination.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('travel_input', '0019_importantfactor_travelpurpose_travelstyle_and_more'),
    ]

    operations = [
        migrations.RunPython(add_default_destinations, remove_default_destinations),
    ] 