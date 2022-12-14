# Generated by Django 4.0.4 on 2022-05-07 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0006_alter_player_inventory_alter_player_unlocked_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField()),
                ('dx', models.IntegerField(blank=True, null=True)),
                ('dy', models.IntegerField(blank=True, null=True)),
                ('x', models.IntegerField(blank=True, null=True)),
                ('y', models.IntegerField(blank=True, null=True)),
                ('unlocked', models.CharField(blank=True, max_length=100, null=True)),
                ('inventory', models.CharField(blank=True, max_length=100, null=True)),
                ('assistant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='records', to='board.assistant')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='records', to='board.player')),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='board.task')),
            ],
        ),
    ]
