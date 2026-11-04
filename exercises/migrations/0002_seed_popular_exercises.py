from django.db import migrations
from exercises.seed_data import POPULAR_EXERCISES
from django.utils.text import slugify


def seed_exercises(apps, schema_editor):
    Exercise = apps.get_model('exercises', 'Exercise')
    for item in POPULAR_EXERCISES:
        base_slug = slugify(item["name"])
        slug = base_slug
        counter = 1
        while Exercise.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        Exercise.objects.get_or_create(
            name=item["name"],
            defaults={
                "slug": slug,
                "category": item["category"],
                "target_muscle_group": item["target_muscle_group"],
                "secondary_muscles": item.get("secondary_muscles", ""),
                "equipment": item["equipment"],
                "instructions": item.get("instructions", ""),
                "is_custom": False,
            }
        )


def reverse_seed_exercises(apps, schema_editor):
    Exercise = apps.get_model('exercises', 'Exercise')
    names = [item["name"] for item in POPULAR_EXERCISES]
    Exercise.objects.filter(name__in=names, is_custom=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_exercises, reverse_seed_exercises),
    ]
