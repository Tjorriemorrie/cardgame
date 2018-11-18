# Generated by Django 2.1.3 on 2018-11-14 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0005_auto_20181114_1926'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='outcome',
        ),
        migrations.AddField(
            model_name='event',
            name='comment',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='error',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='command',
            field=models.CharField(choices=[('status', 'Status'), ('draw', 'Draw'), ('shuffle', 'Shuffle'), ('phase', 'Phase'), ('play', 'Play')], max_length=250),
        ),
    ]
