# Generated by Django 2.2.19 on 2022-04-22 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'admin'), ('user', 'user'), ('moderator', 'moderator')], default='user', max_length=20, verbose_name='статус'),
        ),
    ]
