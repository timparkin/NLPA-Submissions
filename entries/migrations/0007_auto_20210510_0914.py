# Generated by Django 3.1.7 on 2021-05-10 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0006_auto_20210502_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='fullsize_url',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Full Size URL'),
        ),
        migrations.AddField(
            model_name='entry',
            name='thumbnail_url',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Full Size URL'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='category',
            field=models.CharField(blank=True, choices=[('GL', 'Grand Landscape'), ('IA', 'Intimate and Abstract'), ('N', 'Nightscape'), ('A', 'Aerial'), ('P1', 'Portfolio 1'), ('P2', 'Portfolio 2')], default='GL', max_length=128, null=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='photo',
            field=models.ImageField(default='entries/default-entry.png', max_length=500, upload_to='entries/', verbose_name='Entry Photo'),
        ),
    ]