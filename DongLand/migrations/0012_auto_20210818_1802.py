# Generated by Django 3.2.5 on 2021-08-18 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0011_merge_0010_auto_20210813_1831_0010_auto_20210818_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='KW4I734FA7', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='ZLW9TYUDGD', max_length=10),
        ),
    ]
