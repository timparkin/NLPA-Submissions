# Generated by Django 3.1.7 on 2021-05-10 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0010_auto_20210510_1924'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='fullsize_url',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='thumbnail_url',
        ),
        migrations.AlterField(
            model_name='entry',
            name='category',
            field=models.CharField(blank=True, choices=[('GL', 'Grand Landscape'), ('IA', 'Intimate and Abstract'), ('N', 'Nightscape'), ('A', 'Aerial')], default='GL', max_length=128, null=True, verbose_name='Category'),
        ),
    ]
