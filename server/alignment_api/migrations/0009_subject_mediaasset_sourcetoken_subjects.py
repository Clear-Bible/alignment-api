# Generated by Django 4.1.7 on 2023-05-24 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("alignment_api", "0008_alignment_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject_id", models.CharField(max_length=15, unique=True)),
                ("name", models.CharField(max_length=256)),
                ("description", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("media_asset_id", models.CharField(max_length=256)),
                ("dam_id", models.CharField(max_length=128)),
                ("title", models.CharField(max_length=256)),
                ("subtitle", models.CharField(max_length=256)),
                ("description", models.CharField(max_length=256)),
                (
                    "asset_type",
                    models.CharField(
                        choices=[
                            ("PHOTO", "Photo"),
                            ("MAP", "Map"),
                            ("ART", "Art"),
                            ("ARTICLE", "Article"),
                            ("CHART", "Chart"),
                        ],
                        max_length=12,
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        db_column="subject",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="alignment_api.subject",
                        to_field="subject_id",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="sourcetoken",
            name="subjects",
            field=models.ManyToManyField(
                related_name="tokens", to="alignment_api.subject"
            ),
        ),
    ]
