# Generated by Django 3.1.7 on 2021-04-28 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='photos/default-entry.jpg', upload_to='entries/', verbose_name='Entry Photo')),
                ('datetime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Uploaded date')),
                ('description', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Description')),
                ('title', models.CharField(default='Untitled', max_length=128, verbose_name='Title')),
                ('year', models.IntegerField(blank=True, null=True, verbose_name='Competition Year')),
                ('category', models.CharField(blank=True, max_length=128, null=True, verbose_name='Category')),
                ('project_id', models.CharField(max_length=128, verbose_name='Project Identifier')),
                ('internal_notes', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Notes')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['datetime'],
            },
        ),
    ]
