# Generated by Django 4.1.5 on 2023-01-27 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CensusChoropleth', '0002_rename_geolevel_geography_geo_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datum',
            name='value',
            field=models.FloatField(),
        ),
    ]