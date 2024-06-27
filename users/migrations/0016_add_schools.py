from django.db import migrations

def add_schools(apps, schema_editor):
    School = apps.get_model('users', 'School')
    schools = [
        "Academic City University College",
        "Accra Institute of Technology",
        "Adventist College of Education",
        "Akatsi College of Education",
        "Akrokerri College of Education",
        "All Nations University",
        "Ashesi University",
        "BlueCrest University College",
        "Bolgatanga Technical University",
        "Catholic University College of Ghana",
        "Central University",
        "Christian Service University College",
        "College of Agriculture and Natural Resources",
        "DataLink University College",
        "Ensign Global College",
        "Garden City University College",
        "George Grant University of Mines and Technology",
        "Ghana Baptist University College",
        "Ghana Communication Technology University",
        "Ghana Institute of Management and Public Administration",
        "Ghana Military Academy",
        "Ghana-India Kofi Annan Centre of Excellence in ICT",
        "Ho Technical University",
        "Islamic University College, Ghana",
        "Lancaster University Ghana",
        "KAAF University College",
        "Kibi Presbyterian College of Education",
        "Kings University College",
        "Koforidua Technical University",
        "Kumasi Nurses and Midwifery Training School",
        "Kumasi Technical University",
        "Kwame Nkrumah University of Science and Technology",
        "Mampong Technical College of Education",
        "Methodist University College Ghana",
        "Mount Mary College of Education",
        "Nobel International Business School",
        "Pentecost University",
        "Presbyterian University College",
        "Radford University College",
        "Regent University College of Science and Technology",
        "Regional Maritime University",
        "SOS-Hermann Gmeiner International College",
        "Spiritan University College",
        "Sunyani Technical University",
        "Takoradi Technical University",
        "Tamale Technical University",
        "University for Development Studies",
        "University of Cape Coast",
        "University College of Management Studies",
        "University of Education, Winneba",
        "University of Energy and Natural Resources",
        "University of Environment and Sustainable Development",
        "University of Ghana",
        "University of Ghana Business School",
        "University of Health and Allied Sciences",
        "University of Media, Arts and Communication",
        "University of Professional Studies",
        "Wisconsin International University College",
    ]

    for name in schools:
        School.objects.create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_schools),
    ]
