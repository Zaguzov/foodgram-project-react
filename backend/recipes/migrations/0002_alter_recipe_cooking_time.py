# Generated by Django 3.2.6 on 2021-10-04 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Время необходимое для приготовления рецепта', verbose_name='Время приготовления'),
        ),
    ]