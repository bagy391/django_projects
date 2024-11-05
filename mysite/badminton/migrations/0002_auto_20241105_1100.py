# Generated by Django 3.1 on 2024-11-05 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('badminton', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='match_type',
            field=models.CharField(choices=[('RR', 'Round Robin'), ('SF', 'Semi Final'), ('F', 'Final')], default='RR', max_length=2),
        ),
        migrations.AddField(
            model_name='tournament',
            name='is_knockout_stage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournament',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournaments_won', to='badminton.team'),
        ),
    ]
