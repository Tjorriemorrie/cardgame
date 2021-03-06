# Generated by Django 2.1.3 on 2018-12-02 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0008_auto_20181117_2147'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='health',
            new_name='belief',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='pool',
            new_name='crowd',
        ),
        migrations.AlterField(
            model_name='event',
            name='phase',
            field=models.CharField(choices=[('draw', 'Draw'), ('main', 'Main'), ('debate', 'Debate'), ('upkeep', 'Upkeep')], max_length=20),
        ),
        migrations.AlterField(
            model_name='game',
            name='phase',
            field=models.CharField(choices=[('draw', 'Draw'), ('main', 'Main'), ('debate', 'Debate'), ('upkeep', 'Upkeep')], default='draw', max_length=20),
        ),
        migrations.AlterField(
            model_name='gamecard',
            name='slot',
            field=models.CharField(choices=[('deck', 'Deck'), ('hand', 'Hand'), ('table', 'Table')], max_length=10),
        ),
    ]
