# Generated by Django 3.2.5 on 2021-08-19 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0017_auto_20210819_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='2L6A7MRMMN', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='GDHZ2PUNX6', max_length=10),
        ),
    ]