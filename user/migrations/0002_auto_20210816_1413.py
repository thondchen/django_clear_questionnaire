# Generated by Django 3.1.6 on 2021-08-16 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_info',
            name='gender',
            field=models.IntegerField(null=True),
        ),
    ]