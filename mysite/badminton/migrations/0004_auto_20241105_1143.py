# Generated by Django 3.1 on 2024-11-05 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badminton', '0003_auto_20241105_1122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='metadata',
        ),
        migrations.AlterField(
            model_name='match',
            name='match_type',
            field=models.CharField(choices=[('RR', 'Round Robin'), ('SF', 'Semi Final'), ('F', 'Final')], default='RR', max_length=2),
        ),
    ]
