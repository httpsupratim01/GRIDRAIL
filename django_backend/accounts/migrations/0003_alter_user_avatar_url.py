from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_avatar_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar_url",
            field=models.TextField(blank=True),
        ),
    ]
