from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("kitchen", "0005_alter_cook_options_alter_dish_options_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dish",
            old_name="dish_type",
            new_name="dish_category",
        ),
    ]
