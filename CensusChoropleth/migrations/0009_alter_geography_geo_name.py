# Generated by Django 4.1.5 on 2023-01-30 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CensusChoropleth', '0008_alter_geography_dguid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geography',
            name='geo_name',
            field=models.CharField(max_length=100),
        ),
    ]
