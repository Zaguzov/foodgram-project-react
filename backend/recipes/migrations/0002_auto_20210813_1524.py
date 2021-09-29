# Generated by Django 3.2.6 on 2021-08-13 15:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='Автоматически заполняется сегодняшней датой', verbose_name='Дата публикации'),
            preserve_default=False,
        ),
    ]