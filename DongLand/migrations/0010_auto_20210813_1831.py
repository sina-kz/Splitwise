# Generated by Django 3.2.5 on 2021-08-13 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0009_auto_20210813_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='BEX9PXEAOZ', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='SUD9EL9P32', max_length=10),
        ),
    ]
