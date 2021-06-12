# Generated by Django 3.1.7 on 2021-06-05 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0010_auto_20210602_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='payment_upgrade_plan',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Payment Upgrade Plan'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='payment_upgrade_status',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Payment Upgrade Status'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='payment_plan',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Payment Plan'),
        ),
    ]