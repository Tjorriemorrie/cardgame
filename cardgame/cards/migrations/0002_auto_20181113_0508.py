# Generated by Django 2.1.3 on 2018-11-13 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carditem',
            name='card',
        ),
        migrations.RemoveField(
            model_name='deck',
            name='carditem_ptr',
        ),
        migrations.RemoveField(
            model_name='deck',
            name='player',
        ),
        migrations.RemoveField(
            model_name='grave',
            name='carditem_ptr',
        ),
        migrations.RemoveField(
            model_name='grave',
            name='player',
        ),
        migrations.RemoveField(
            model_name='hand',
            name='carditem_ptr',
        ),
        migrations.RemoveField(
            model_name='hand',
            name='player',
        ),
        migrations.DeleteModel(
            name='CardItem',
        ),
        migrations.DeleteModel(
            name='Deck',
        ),
        migrations.DeleteModel(
            name='Grave',
        ),
        migrations.DeleteModel(
            name='Hand',
        ),
    ]