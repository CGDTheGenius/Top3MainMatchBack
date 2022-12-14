# Generated by Django 4.0.4 on 2022-05-07 03:27

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('board', '0004_wall_alter_player_options_alter_task_error_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='inventory',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='player',
            name='unlocked',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='board.player'),
        ),
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('partner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assistant', to='board.player')),
            ],
            options={
                'verbose_name': 'Assistant',
                'verbose_name_plural': 'Assistants',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='assistant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='board.assistant'),
        ),
    ]
