# Generated by Django 4.0.4 on 2022-05-07 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0007_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='inventory',
            field=models.CharField(blank=True, default='TOWER', max_length=100),
        ),
        migrations.AlterField(
            model_name='player',
            name='unlocked',
            field=models.CharField(blank=True, default='FAKE/TOWER', max_length=100),
        ),
    ]
