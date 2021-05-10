# Generated by Django 3.1.7 on 2021-05-10 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0011_auto_20210510_2029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='photo_stats',
        ),
        migrations.AddField(
            model_name='entry',
            name='photo_dimensions',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Photo Dimensions'),
        ),
        migrations.AddField(
            model_name='entry',
            name='photo_size',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Photo Size'),
        ),
    ]
