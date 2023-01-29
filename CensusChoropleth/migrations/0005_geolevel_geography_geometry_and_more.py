# Generated by Django 4.1.5 on 2023-01-28 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CensusChoropleth', '0004_alter_datum_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='geography',
            name='geometry',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='geography',
            name='geo_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CensusChoropleth.geolevel'),
        ),
    ]
