# Generated by Django 4.1.3 on 2022-11-20 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='description',
            field=models.TextField(default='よろしくお願いします。'),
        ),
    ]
