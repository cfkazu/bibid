# Generated by Django 4.1.3 on 2022-11-25 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0009_imagemulmodel_specificimagemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specificimagemodel',
            name='MotoImage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='server.imagemulmodel'),
        ),
    ]
